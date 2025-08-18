use crate::error::{Result, XacroError};
use indexmap::IndexMap;
use std::collections::HashMap;

#[derive(Debug, Clone)]
pub struct SymbolTable {
    symbols: IndexMap<String, String>,
    parent: Option<Box<SymbolTable>>,
    substitution_args: HashMap<String, String>,
    unevaluated: std::collections::HashSet<String>,
}

impl Default for SymbolTable {
    fn default() -> Self {
        Self::new()
    }
}

impl SymbolTable {
    pub fn new() -> Self {
        let mut table = Self {
            symbols: IndexMap::new(),
            parent: None,
            substitution_args: HashMap::new(),
            unevaluated: std::collections::HashSet::new(),
        };

        // Add built-in symbols
        table.init_builtins();
        table
    }

    pub fn with_parent(parent: SymbolTable) -> Self {
        Self {
            symbols: IndexMap::new(),
            parent: Some(Box::new(parent)),
            substitution_args: HashMap::new(),
            unevaluated: std::collections::HashSet::new(),
        }
    }

    fn init_builtins(&mut self) {
        // Built-in math functions
        self.symbols
            .insert("pi".to_string(), std::f64::consts::PI.to_string());
        self.symbols
            .insert("e".to_string(), std::f64::consts::E.to_string());

        // Built-in boolean values
        self.symbols.insert("True".to_string(), "true".to_string());
        self.symbols
            .insert("False".to_string(), "false".to_string());
    }

    pub fn set(&mut self, name: String, value: String) {
        self.symbols.insert(name, value);
    }

    pub fn get(&self, name: &str) -> Option<&String> {
        if let Some(value) = self.symbols.get(name) {
            Some(value)
        } else if let Some(parent) = &self.parent {
            parent.get(name)
        } else {
            None
        }
    }

    pub fn contains(&self, name: &str) -> bool {
        self.symbols.contains_key(name) || self.parent.as_ref().is_some_and(|p| p.contains(name))
    }

    pub fn remove(&mut self, name: &str) -> Option<String> {
        self.symbols.shift_remove(name)
    }

    pub fn set_substitution_args(&mut self, args: HashMap<String, String>) {
        self.substitution_args = args;
    }

    pub fn get_substitution_arg(&self, name: &str) -> Option<&String> {
        self.substitution_args.get(name)
    }

    pub fn resolve(&mut self, name: &str) -> Result<String> {
        if self.unevaluated.contains(name) {
            return Err(XacroError::CircularDefinition(name.to_string()));
        }

        if let Some(value) = self.get(name) {
            Ok(value.clone())
        } else {
            Err(XacroError::UndefinedSymbol(name.to_string()))
        }
    }

    pub fn keys(&self) -> impl Iterator<Item = &String> {
        self.symbols.keys()
    }

    pub fn values(&self) -> impl Iterator<Item = &String> {
        self.symbols.values()
    }

    pub fn iter(&self) -> impl Iterator<Item = (&String, &String)> {
        self.symbols.iter()
    }

    pub fn get_all_keys(&self) -> Vec<String> {
        let mut keys = self.symbols.keys().cloned().collect::<Vec<_>>();
        if let Some(parent) = &self.parent {
            keys.extend(parent.get_all_keys());
        }
        keys.sort();
        keys.dedup();
        keys
    }
}
