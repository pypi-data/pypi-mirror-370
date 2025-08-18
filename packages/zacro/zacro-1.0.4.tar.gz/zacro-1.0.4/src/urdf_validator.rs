use petgraph::algo::{connected_components, is_cyclic_directed};
use petgraph::graph::UnGraph;
use petgraph::visit::Dfs;
use std::collections::{HashMap, HashSet};
use xmltree::{Element, XMLNode};

#[derive(Debug, Clone)]
pub struct Link {
    pub name: String,
    pub element: Element,
}

#[derive(Debug, Clone)]
pub struct Joint {
    pub name: String,
    pub parent: String,
    pub child: String,
    pub joint_type: String,
    pub element: Element,
}

#[derive(Debug)]
pub struct ValidationError {
    pub message: String,
}

impl std::fmt::Display for ValidationError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "{}", self.message)
    }
}

impl std::error::Error for ValidationError {}

#[derive(Debug)]
pub struct ValidationResult {
    pub is_valid: bool,
    pub errors: Vec<String>,
    pub warnings: Vec<String>,
    pub summary: ValidationSummary,
}

#[derive(Debug)]
pub struct ValidationSummary {
    pub links_count: usize,
    pub joints_count: usize,
    pub base_links: Vec<String>,
    pub end_links: Vec<String>,
    pub connected_components: usize,
}

pub struct URDFValidator {
    links: HashMap<String, Link>,
    joints: HashMap<String, Joint>,
    parent_child_map: HashMap<String, String>, // child -> parent
    child_parent_map: HashMap<String, Vec<String>>, // parent -> [children]
}

impl Default for URDFValidator {
    fn default() -> Self {
        Self::new()
    }
}

impl URDFValidator {
    pub fn new() -> Self {
        Self {
            links: HashMap::new(),
            joints: HashMap::new(),
            parent_child_map: HashMap::new(),
            child_parent_map: HashMap::new(),
        }
    }

    pub fn parse_urdf(&mut self, urdf_content: &str) -> Result<(), ValidationError> {
        let root = Element::parse(urdf_content.as_bytes()).map_err(|e| ValidationError {
            message: format!("Failed to parse URDF XML: {e}"),
        })?;

        if root.name != "robot" {
            return Err(ValidationError {
                message: format!("Expected 'robot' root element, got '{}'", root.name),
            });
        }

        // Clear previous data
        self.links.clear();
        self.joints.clear();
        self.parent_child_map.clear();
        self.child_parent_map.clear();

        // Extract links
        for child in &root.children {
            if let XMLNode::Element(element) = child {
                if element.name == "link" {
                    let name = element
                        .attributes
                        .get("name")
                        .ok_or_else(|| ValidationError {
                            message: "Found link without 'name' attribute".to_string(),
                        })?;

                    self.links.insert(
                        name.clone(),
                        Link {
                            name: name.clone(),
                            element: element.clone(),
                        },
                    );
                }
            }
        }

        // Extract joints
        for child in &root.children {
            if let XMLNode::Element(element) = child {
                if element.name == "joint" {
                    let joint_name =
                        element
                            .attributes
                            .get("name")
                            .ok_or_else(|| ValidationError {
                                message: "Found joint without 'name' attribute".to_string(),
                            })?;

                    let parent_elem = element
                        .children
                        .iter()
                        .find_map(|child| {
                            if let XMLNode::Element(elem) = child {
                                if elem.name == "parent" {
                                    Some(elem)
                                } else {
                                    None
                                }
                            } else {
                                None
                            }
                        })
                        .ok_or_else(|| ValidationError {
                            message: format!("Joint '{joint_name}' missing parent element"),
                        })?;

                    let child_elem = element
                        .children
                        .iter()
                        .find_map(|child| {
                            if let XMLNode::Element(elem) = child {
                                if elem.name == "child" {
                                    Some(elem)
                                } else {
                                    None
                                }
                            } else {
                                None
                            }
                        })
                        .ok_or_else(|| ValidationError {
                            message: format!("Joint '{joint_name}' missing child element"),
                        })?;

                    let parent_link =
                        parent_elem
                            .attributes
                            .get("link")
                            .ok_or_else(|| ValidationError {
                                message: format!(
                                    "Joint '{joint_name}' parent missing 'link' attribute"
                                ),
                            })?;

                    let child_link =
                        child_elem
                            .attributes
                            .get("link")
                            .ok_or_else(|| ValidationError {
                                message: format!(
                                    "Joint '{joint_name}' child missing 'link' attribute"
                                ),
                            })?;

                    let joint_type = element
                        .attributes
                        .get("type")
                        .unwrap_or(&"unknown".to_string())
                        .clone();

                    self.joints.insert(
                        joint_name.clone(),
                        Joint {
                            name: joint_name.clone(),
                            parent: parent_link.clone(),
                            child: child_link.clone(),
                            joint_type,
                            element: element.clone(),
                        },
                    );

                    // Build parent-child relationships
                    self.parent_child_map
                        .insert(child_link.clone(), parent_link.clone());
                    self.child_parent_map
                        .entry(parent_link.clone())
                        .or_default()
                        .push(child_link.clone());
                }
            }
        }

        Ok(())
    }

    pub fn find_base_links(&self) -> Vec<String> {
        self.links
            .keys()
            .filter(|link_name| !self.parent_child_map.contains_key(*link_name))
            .cloned()
            .collect()
    }

    pub fn find_end_links(&self) -> Vec<String> {
        self.links
            .keys()
            .filter(|link_name| !self.child_parent_map.contains_key(*link_name))
            .cloned()
            .collect()
    }

    pub fn find_connected_components(&self) -> Vec<Vec<String>> {
        let mut graph = UnGraph::new_undirected();
        let mut node_indices = HashMap::new();

        // Add all links as nodes
        for link_name in self.links.keys() {
            let index = graph.add_node(link_name.clone());
            node_indices.insert(link_name.clone(), index);
        }

        // Add edges for joints (undirected for connectivity check)
        for joint in self.joints.values() {
            if let (Some(&parent_idx), Some(&child_idx)) = (
                node_indices.get(&joint.parent),
                node_indices.get(&joint.child),
            ) {
                graph.add_edge(parent_idx, child_idx, ());
            }
        }

        let component_count = connected_components(&graph);
        let mut components = vec![Vec::new(); component_count];
        let mut visited = HashSet::new();

        for &node_idx in node_indices.values() {
            if visited.contains(&node_idx) {
                continue;
            }

            let mut component = Vec::new();
            let mut dfs = Dfs::new(&graph, node_idx);

            while let Some(nx) = dfs.next(&graph) {
                if !visited.contains(&nx) {
                    visited.insert(nx);
                    if let Some(node_weight) = graph.node_weight(nx) {
                        component.push(node_weight.clone());
                    }
                }
            }

            if !component.is_empty() {
                for comp in components.iter_mut() {
                    if comp.is_empty() {
                        *comp = component;
                        break;
                    }
                }
            }
        }

        components.into_iter().filter(|c| !c.is_empty()).collect()
    }

    pub fn detect_cycles(&self) -> Vec<Vec<String>> {
        use petgraph::Graph as DirectedGraph;

        let mut graph = DirectedGraph::new();
        let mut node_indices = HashMap::new();

        // Add all links as nodes
        for link_name in self.links.keys() {
            let index = graph.add_node(link_name.clone());
            node_indices.insert(link_name.clone(), index);
        }

        // Add directed edges for joints (parent -> child)
        for joint in self.joints.values() {
            if let (Some(&parent_idx), Some(&child_idx)) = (
                node_indices.get(&joint.parent),
                node_indices.get(&joint.child),
            ) {
                graph.add_edge(parent_idx, child_idx, ());
            }
        }

        // Use petgraph's cycle detection
        let mut cycles = Vec::new();
        if is_cyclic_directed(&graph) {
            // Simple cycle detection - for now just report that cycles exist
            // More sophisticated cycle finding would require additional implementation
            cycles.push(vec!["Cycle detected".to_string()]);
        }

        cycles
    }

    pub fn validate_link_references(&self) -> Vec<String> {
        let mut errors = Vec::new();

        for joint in self.joints.values() {
            if !self.links.contains_key(&joint.parent) {
                errors.push(format!(
                    "Joint '{}' references non-existent parent link '{}'",
                    joint.name, joint.parent
                ));
            }

            if !self.links.contains_key(&joint.child) {
                errors.push(format!(
                    "Joint '{}' references non-existent child link '{}'",
                    joint.name, joint.child
                ));
            }
        }

        errors
    }

    pub fn validate(
        &mut self,
        urdf_content: &str,
        verbose: bool,
    ) -> Result<ValidationResult, ValidationError> {
        self.parse_urdf(urdf_content)?;

        let mut errors = Vec::new();
        let mut warnings = Vec::new();

        // Check 1: Validate link references
        let link_errors = self.validate_link_references();
        errors.extend(link_errors);

        // Check 2: Find connected components
        let components = self.find_connected_components();
        if components.len() > 1 {
            let mut error_msg = format!(
                "Links are not all connected. Found {} disconnected components:",
                components.len()
            );
            for (i, component) in components.iter().enumerate() {
                let mut sorted_component = component.clone();
                sorted_component.sort();
                error_msg.push_str(&format!(
                    "\n  Component {}: {}",
                    i + 1,
                    sorted_component.join(", ")
                ));
            }
            errors.push(error_msg);
        }

        // Check 3: Detect cycles
        let cycles = self.detect_cycles();
        if !cycles.is_empty() {
            for cycle in cycles {
                if cycle.len() == 1 && cycle[0] == "Cycle detected" {
                    errors.push("Detected cycle in link graph".to_string());
                } else {
                    let cycle_str = cycle.join(" -> ");
                    errors.push(format!("Detected cycle in link graph: {cycle_str}"));
                }
            }
        }

        // Check 4: Base link validation
        let base_links = self.find_base_links();
        if base_links.is_empty() {
            errors.push(
                "No base link found (all links have parents - this creates a cycle)".to_string(),
            );
        } else if base_links.len() > 1 {
            let base_links_str = base_links
                .iter()
                .map(|link| format!("'{link}'"))
                .collect::<Vec<_>>()
                .join(", ");
            errors.push(format!(
                "Multiple base links found: {base_links_str}. A valid URDF should have exactly one base link."
            ));
        }

        // Check 5: End links (warnings only)
        let end_links = self.find_end_links();
        if end_links.is_empty() {
            warnings.push("No end links found (all links have children)".to_string());
        }

        let summary = ValidationSummary {
            links_count: self.links.len(),
            joints_count: self.joints.len(),
            base_links: base_links.clone(),
            end_links: end_links.clone(),
            connected_components: components.len(),
        };

        // Print validation summary if verbose
        if verbose {
            eprintln!("URDF Validation Summary:");
            eprintln!("  Links: {}", summary.links_count);
            eprintln!("  Joints: {}", summary.joints_count);
            eprintln!(
                "  Base links: {} ({})",
                base_links.len(),
                if base_links.is_empty() {
                    "None".to_string()
                } else {
                    base_links.join(", ")
                }
            );
            eprintln!(
                "  End links: {} ({})",
                end_links.len(),
                if end_links.is_empty() {
                    "None".to_string()
                } else {
                    end_links.join(", ")
                }
            );
            eprintln!("  Connected components: {}", components.len());

            if !warnings.is_empty() {
                eprintln!("Warnings:");
                for warning in &warnings {
                    eprintln!("  - {warning}");
                }
            }

            if !errors.is_empty() {
                eprintln!("Validation Errors:");
                for error in &errors {
                    eprintln!("  - {error}");
                }
            } else {
                eprintln!("✓ All validation checks passed!");
            }
        }

        Ok(ValidationResult {
            is_valid: errors.is_empty(),
            errors,
            warnings,
            summary,
        })
    }
}

impl URDFValidator {
    pub fn print_link_tree(&self) -> String {
        let base_links = self.find_base_links();

        if base_links.is_empty() {
            return "No base links found - cannot build tree structure".to_string();
        }

        let mut output = String::new();
        output.push_str("URDF Link Tree Structure:\n");

        for (i, base_link) in base_links.iter().enumerate() {
            if i > 0 {
                output.push('\n');
            }
            self.print_subtree(base_link, "", true, &mut output);
        }

        output
    }

    fn print_subtree(&self, link_name: &str, prefix: &str, is_last: bool, output: &mut String) {
        // Print current link
        let branch = if is_last { "└── " } else { "├── " };
        output.push_str(&format!("{prefix}{branch}{link_name}\n"));

        // Find children of this link
        let children = self
            .child_parent_map
            .get(link_name)
            .cloned()
            .unwrap_or_default();

        // Print children
        for (i, child) in children.iter().enumerate() {
            let is_last_child = i == children.len() - 1;
            let new_prefix = if is_last {
                format!("{prefix}    ")
            } else {
                format!("{prefix}│   ")
            };

            self.print_subtree(child, &new_prefix, is_last_child, output);
        }
    }
}

pub fn validate_urdf(
    urdf_content: &str,
    verbose: bool,
) -> Result<ValidationResult, ValidationError> {
    let mut validator = URDFValidator::new();
    validator.validate(urdf_content, verbose)
}

pub fn print_urdf_tree(urdf_content: &str) -> Result<String, ValidationError> {
    let mut validator = URDFValidator::new();
    validator.parse_urdf(urdf_content)?;
    Ok(validator.print_link_tree())
}
