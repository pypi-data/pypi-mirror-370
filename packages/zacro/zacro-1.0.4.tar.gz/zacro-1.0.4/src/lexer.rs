use regex::Regex;

#[derive(Debug, Clone, PartialEq)]
pub enum Token {
    Text(String),
    Expression(String),
    Extension(String),
    DollarBrace(String),
}

pub struct Lexer {
    input: String,
    position: usize,
    dollar_dollar_brace_re: Regex,
    expr_re: Regex,
    extension_re: Regex,
    text_re: Regex,
}

impl Lexer {
    pub fn new(input: &str) -> Self {
        Self {
            input: input.to_string(),
            position: 0,
            dollar_dollar_brace_re: Regex::new(r"^\$\$+(\{|\()").unwrap(),
            expr_re: Regex::new(r"^\$\{[^}]*\}").unwrap(),
            extension_re: Regex::new(r"^\$\([^)]*\)").unwrap(),
            text_re: Regex::new(r"[^$]+|\$[^{($]+|\$$").unwrap(),
        }
    }

    #[allow(clippy::should_implement_trait)]
    pub fn next(&mut self) -> Option<Token> {
        if self.position >= self.input.len() {
            return None;
        }

        let remaining = &self.input[self.position..];

        // Check for multiple $ followed by { or (
        if let Some(mat) = self.dollar_dollar_brace_re.find(remaining) {
            let matched = mat.as_str();
            self.position += mat.end();
            return Some(Token::DollarBrace(matched[1..].to_string())); // Remove first $
        }

        // Check for expressions ${...}
        if let Some(mat) = self.expr_re.find(remaining) {
            let matched = mat.as_str();
            self.position += mat.end();
            let expr = &matched[2..matched.len() - 1]; // Remove ${ and }
            return Some(Token::Expression(expr.to_string()));
        }

        // Check for extensions $(...)
        if let Some(mat) = self.extension_re.find(remaining) {
            let matched = mat.as_str();
            self.position += mat.end();
            let ext = &matched[2..matched.len() - 1]; // Remove $( and )
            return Some(Token::Extension(ext.to_string()));
        }

        // Check for text
        if let Some(mat) = self.text_re.find(remaining) {
            let matched = mat.as_str();
            self.position += mat.end();
            return Some(Token::Text(matched.to_string()));
        }

        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_lexer_simple_text() {
        let mut lexer = Lexer::new("hello world");
        assert_eq!(lexer.next(), Some(Token::Text("hello world".to_string())));
        assert_eq!(lexer.next(), None);
    }

    #[test]
    fn test_lexer_expression() {
        let mut lexer = Lexer::new("${foo}");
        assert_eq!(lexer.next(), Some(Token::Expression("foo".to_string())));
        assert_eq!(lexer.next(), None);
    }

    #[test]
    fn test_lexer_extension() {
        let mut lexer = Lexer::new("$(find package)");
        assert_eq!(
            lexer.next(),
            Some(Token::Extension("find package".to_string()))
        );
        assert_eq!(lexer.next(), None);
    }

    #[test]
    fn test_lexer_mixed() {
        let mut lexer = Lexer::new("Hello ${name}, $(cwd)!");
        assert_eq!(lexer.next(), Some(Token::Text("Hello ".to_string())));
        assert_eq!(lexer.next(), Some(Token::Expression("name".to_string())));
        assert_eq!(lexer.next(), Some(Token::Text(", ".to_string())));
        assert_eq!(lexer.next(), Some(Token::Extension("cwd".to_string())));
        assert_eq!(lexer.next(), Some(Token::Text("!".to_string())));
        assert_eq!(lexer.next(), None);
    }
}
