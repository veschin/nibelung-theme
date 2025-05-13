use std::env;
use std::fs;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = env::args().collect();

    if args.len() < 2 {
        eprintln!("Usage: {} <filename>", args[0]);
        std::process::exit(1);
    }

    let filename = &args[1];

    let content = fs::read_to_string(filename)?;

    let stats = TextStats::analyze(&content);

    println!("File: {}", filename);
    println!("Lines: {}", stats.lines);
    println!("Words: {}", stats.words);
    println!("Characters: {}", stats.characters);

    Ok(())
}

struct TextStats {
    lines: usize,
    words: usize,
    characters: usize,
}

// Text Stats Comment
impl TextStats {
    fn analyze(text: &str) -> Self {
        let lines = text.lines().count();
        let words = text.split_whitespace().count();
        let characters = text.chars().count();

        TextStats {
            lines,
            words,
            characters,
        }
    }
}
