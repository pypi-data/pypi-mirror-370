use std::collections::HashMap;
use xmltree::Element;
// use crate::error::{Result, XacroError};

#[derive(Debug, Clone)]
pub struct Macro {
    pub name: String,
    pub params: Vec<String>,
    pub defaults: HashMap<String, String>,
    pub body: Element,
}

impl Macro {
    pub fn new(name: String, params_str: &str, body: Element) -> Self {
        let (params, defaults) = Self::parse_params(params_str);

        Self {
            name,
            params,
            defaults,
            body,
        }
    }

    fn parse_params(params_str: &str) -> (Vec<String>, HashMap<String, String>) {
        let mut params = Vec::new();
        let mut defaults = HashMap::new();

        if params_str.trim().is_empty() {
            return (params, defaults);
        }

        for param in params_str.split_whitespace() {
            if let Some(eq_pos) = param.find(':') {
                // Parameter with default value: "param:=default"
                let param_name = param[..eq_pos].trim();
                let default_value =
                    if param.len() > eq_pos + 2 && &param[eq_pos..eq_pos + 2] == ":=" {
                        param[eq_pos + 2..].trim()
                    } else {
                        param[eq_pos + 1..].trim()
                    };

                params.push(param_name.to_string());
                defaults.insert(param_name.to_string(), default_value.to_string());
            } else {
                // Parameter without default value
                params.push(param.to_string());
            }
        }

        (params, defaults)
    }

    pub fn has_param(&self, name: &str) -> bool {
        self.params.contains(&name.to_string())
    }

    pub fn get_default(&self, name: &str) -> Option<&String> {
        self.defaults.get(name)
    }
}

#[derive(Debug)]
pub struct MacroTable {
    macros: HashMap<String, Macro>,
}

impl Default for MacroTable {
    fn default() -> Self {
        Self::new()
    }
}

impl MacroTable {
    pub fn new() -> Self {
        Self {
            macros: HashMap::new(),
        }
    }

    pub fn insert(&mut self, name: String, macro_def: Macro) {
        self.macros.insert(name, macro_def);
    }

    pub fn get(&self, name: &str) -> Option<&Macro> {
        self.macros.get(name)
    }

    pub fn contains(&self, name: &str) -> bool {
        self.macros.contains_key(name)
    }

    pub fn remove(&mut self, name: &str) -> Option<Macro> {
        self.macros.remove(name)
    }

    pub fn keys(&self) -> impl Iterator<Item = &String> {
        self.macros.keys()
    }

    pub fn values(&self) -> impl Iterator<Item = &Macro> {
        self.macros.values()
    }

    pub fn iter(&self) -> impl Iterator<Item = (&String, &Macro)> {
        self.macros.iter()
    }
}
