use thiserror::Error;

#[derive(Error, Debug)]
pub enum XacroError {
    #[error("IO error: {0}")]
    Io(#[from] std::io::Error),

    #[error("Parse error: {0}")]
    Parse(String),

    #[error("Evaluation error: {0}")]
    Eval(String),

    #[error("Macro error: {0}")]
    Macro(String),

    #[error("Include error: {0}")]
    Include(String),

    #[error("Property error: {0}")]
    Property(String),

    #[error("Type error: {0}")]
    Type(String),

    #[error("Undefined symbol: {0}")]
    UndefinedSymbol(String),

    #[error("Circular definition: {0}")]
    CircularDefinition(String),
}

pub type Result<T> = std::result::Result<T, XacroError>;
