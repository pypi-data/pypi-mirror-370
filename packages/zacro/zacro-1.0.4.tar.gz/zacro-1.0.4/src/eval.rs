use crate::error::{Result, XacroError};
use crate::lexer::{Lexer, Token};
use crate::symbols::SymbolTable;
use crate::utils::resolve_package_path;
use regex::Regex;
use std::path::Path;

pub fn eval_text(text: &str, symbols: &SymbolTable, current_file: Option<&Path>) -> Result<String> {
    let mut lexer = Lexer::new(text);
    let mut results = Vec::new();

    while let Some(token) = lexer.next() {
        match token {
            Token::Text(s) => results.push(s),
            Token::Expression(expr) => {
                let value = eval_expression(&expr, symbols)?;
                results.push(value);
            }
            Token::Extension(ext) => {
                let value = eval_extension(&ext, symbols, current_file)?;
                results.push(value);
            }
            Token::DollarBrace(s) => {
                results.push(s);
            }
        }
    }

    if results.len() == 1 {
        Ok(results[0].clone())
    } else {
        Ok(results.join(""))
    }
}

fn eval_expression(expr: &str, symbols: &SymbolTable) -> Result<String> {
    // Simple expression evaluator
    // This is a simplified version - a full implementation would need a proper parser

    let expr = expr.trim();

    // Handle simple variable references
    if is_simple_identifier(expr) {
        if let Some(value) = symbols.get(expr) {
            return Ok(value.clone());
        } else {
            return Err(XacroError::UndefinedSymbol(expr.to_string()));
        }
    }

    // Handle math expressions
    if let Ok(result) = eval_math_expression(expr, symbols) {
        return Ok(result);
    }

    // Handle string literals
    if expr.starts_with('"') && expr.ends_with('"') {
        return Ok(expr[1..expr.len() - 1].to_string());
    }

    if expr.starts_with('\'') && expr.ends_with('\'') {
        return Ok(expr[1..expr.len() - 1].to_string());
    }

    // Handle boolean literals
    match expr {
        "true" | "True" => return Ok("true".to_string()),
        "false" | "False" => return Ok("false".to_string()),
        _ => {}
    }

    // Handle numeric literals
    if let Ok(num) = expr.parse::<f64>() {
        return Ok(num.to_string());
    }

    // If all else fails, try to evaluate as a string substitution
    eval_text_substitution(expr, symbols)
}

fn eval_math_expression(expr: &str, symbols: &SymbolTable) -> Result<String> {
    let expr = expr.trim();

    // Handle parentheses first
    if let Some(result) = eval_parentheses(expr, symbols)? {
        return Ok(result);
    }

    // Handle operators with proper precedence (lowest to highest)
    // Addition and subtraction (lowest precedence)
    if let Some(pos) = find_operator_outside_parens(expr, '+') {
        let left = eval_expression(&expr[..pos], symbols)?;
        let right = eval_expression(&expr[pos + 1..], symbols)?;
        if let (Ok(l), Ok(r)) = (left.parse::<f64>(), right.parse::<f64>()) {
            return Ok((l + r).to_string());
        }
    }

    if let Some(pos) = find_operator_outside_parens(expr, '-') {
        if pos > 0 {
            // Not a negative number at the start
            let left = eval_expression(&expr[..pos], symbols)?;
            let right = eval_expression(&expr[pos + 1..], symbols)?;
            if let (Ok(l), Ok(r)) = (left.parse::<f64>(), right.parse::<f64>()) {
                return Ok((l - r).to_string());
            }
        } else if pos == 0 {
            // Handle negative number at start: -expr becomes 0 - expr
            let right = eval_expression(&expr[1..], symbols)?;
            if let Ok(r) = right.parse::<f64>() {
                return Ok((-r).to_string());
            }
        }
    }

    // Multiplication and division (higher precedence)
    if let Some(pos) = find_operator_outside_parens(expr, '*') {
        let left = eval_expression(&expr[..pos], symbols)?;
        let right = eval_expression(&expr[pos + 1..], symbols)?;
        if let (Ok(l), Ok(r)) = (left.parse::<f64>(), right.parse::<f64>()) {
            return Ok((l * r).to_string());
        }
    }

    if let Some(pos) = find_operator_outside_parens(expr, '/') {
        let left = eval_expression(&expr[..pos], symbols)?;
        let right = eval_expression(&expr[pos + 1..], symbols)?;
        if let (Ok(l), Ok(r)) = (left.parse::<f64>(), right.parse::<f64>()) {
            if r != 0.0 {
                return Ok((l / r).to_string());
            } else {
                return Err(XacroError::Eval("Division by zero".to_string()));
            }
        }
    }

    // Handle function calls
    if expr.contains('(') && expr.ends_with(')') && !expr.starts_with('(') {
        return eval_function_call(expr, symbols);
    }

    Err(XacroError::Eval(format!(
        "Cannot evaluate math expression: {expr}"
    )))
}

fn eval_parentheses(expr: &str, symbols: &SymbolTable) -> Result<Option<String>> {
    // Handle parentheses by finding the outermost ones and evaluating the content
    if expr.starts_with('(') && expr.ends_with(')') {
        let inner = &expr[1..expr.len() - 1];
        return Ok(Some(eval_expression(inner, symbols)?));
    }
    Ok(None)
}

fn find_operator_outside_parens(expr: &str, op: char) -> Option<usize> {
    let mut paren_depth = 0;
    let mut last_pos = None;

    for (i, c) in expr.char_indices().rev() {
        match c {
            ')' => paren_depth += 1,
            '(' => paren_depth -= 1,
            _ if c == op && paren_depth == 0 => {
                last_pos = Some(i);
            }
            _ => {}
        }
    }

    last_pos
}

fn eval_function_call(expr: &str, symbols: &SymbolTable) -> Result<String> {
    let paren_pos = expr
        .find('(')
        .ok_or_else(|| XacroError::Eval("Invalid function call".to_string()))?;

    let func_name = expr[..paren_pos].trim();
    let args_str = &expr[paren_pos + 1..expr.len() - 1];

    match func_name {
        "sin" => {
            let arg = eval_expression(args_str, symbols)?;
            let num: f64 = arg
                .parse()
                .map_err(|_| XacroError::Type("Expected number".to_string()))?;
            Ok(libm::sin(num).to_string())
        }
        "cos" => {
            let arg = eval_expression(args_str, symbols)?;
            let num: f64 = arg
                .parse()
                .map_err(|_| XacroError::Type("Expected number".to_string()))?;
            Ok(libm::cos(num).to_string())
        }
        "tan" => {
            let arg = eval_expression(args_str, symbols)?;
            let num: f64 = arg
                .parse()
                .map_err(|_| XacroError::Type("Expected number".to_string()))?;
            Ok(libm::tan(num).to_string())
        }
        "sqrt" => {
            let arg = eval_expression(args_str, symbols)?;
            let num: f64 = arg
                .parse()
                .map_err(|_| XacroError::Type("Expected number".to_string()))?;
            Ok(libm::sqrt(num).to_string())
        }
        "abs" => {
            let arg = eval_expression(args_str, symbols)?;
            let num: f64 = arg
                .parse()
                .map_err(|_| XacroError::Type("Expected number".to_string()))?;
            Ok(num.abs().to_string())
        }
        "min" => {
            let args: Vec<&str> = args_str.split(',').collect();
            if args.len() < 2 {
                return Err(XacroError::Eval(
                    "min() requires at least 2 arguments".to_string(),
                ));
            }
            let mut min_val = f64::INFINITY;
            for arg in args {
                let val = eval_expression(arg.trim(), symbols)?;
                let num: f64 = val
                    .parse()
                    .map_err(|_| XacroError::Type("Expected number".to_string()))?;
                min_val = min_val.min(num);
            }
            Ok(min_val.to_string())
        }
        "max" => {
            let args: Vec<&str> = args_str.split(',').collect();
            if args.len() < 2 {
                return Err(XacroError::Eval(
                    "max() requires at least 2 arguments".to_string(),
                ));
            }
            let mut max_val = f64::NEG_INFINITY;
            for arg in args {
                let val = eval_expression(arg.trim(), symbols)?;
                let num: f64 = val
                    .parse()
                    .map_err(|_| XacroError::Type("Expected number".to_string()))?;
                max_val = max_val.max(num);
            }
            Ok(max_val.to_string())
        }
        _ => Err(XacroError::Eval(format!("Unknown function: {func_name}"))),
    }
}

fn eval_extension(
    ext: &str,
    _symbols: &SymbolTable,
    current_file: Option<&Path>,
) -> Result<String> {
    // Handle ROS substitution arguments like $(find package_name)
    let ext_trimmed = ext.trim();

    if ext_trimmed == "cwd" {
        if let Ok(cwd) = std::env::current_dir() {
            Ok(cwd.to_string_lossy().to_string())
        } else {
            Err(XacroError::Eval("Cannot get current directory".to_string()))
        }
    } else if ext_trimmed.starts_with("find ") {
        // Handle $(find package_name)
        let package_name = ext_trimmed.strip_prefix("find ").unwrap().trim();

        // Get base path from current file or use current directory
        let base_path = if let Some(current) = current_file {
            current.parent().unwrap_or_else(|| Path::new("."))
        } else {
            Path::new(".")
        };

        if let Some(package_path) = resolve_package_path(package_name, base_path) {
            Ok(package_path.to_string_lossy().to_string())
        } else {
            Err(XacroError::Eval(format!(
                "Cannot find package: {package_name}"
            )))
        }
    } else if ext_trimmed.starts_with("arg ") {
        // Handle $(arg argument_name)
        let arg_name = ext_trimmed.strip_prefix("arg ").unwrap().trim();

        // Look up argument in symbol table
        if let Some(value) = _symbols.get(arg_name) {
            Ok(value.clone())
        } else {
            // Return default value "false" for missing arguments (common in ROS)
            Ok("false".to_string())
        }
    } else {
        // For other extensions, return as-is
        Ok(format!("$({ext})"))
    }
}

fn eval_text_substitution(text: &str, symbols: &SymbolTable) -> Result<String> {
    // Replace variable references in text
    let re = Regex::new(r"\$\{([^}]+)\}").unwrap();
    let mut result = text.to_string();

    for cap in re.captures_iter(text) {
        let var_name = &cap[1];
        if let Some(value) = symbols.get(var_name) {
            result = result.replace(&cap[0], value);
        } else {
            return Err(XacroError::UndefinedSymbol(var_name.to_string()));
        }
    }

    Ok(result)
}

fn is_simple_identifier(s: &str) -> bool {
    !s.is_empty()
        && s.chars().all(|c| c.is_alphanumeric() || c == '_')
        && !s.chars().next().unwrap().is_ascii_digit()
}
