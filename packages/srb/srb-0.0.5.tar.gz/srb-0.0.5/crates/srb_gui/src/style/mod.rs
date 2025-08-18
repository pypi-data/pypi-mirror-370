pub use visuals::{dark as dark_visuals, light as light_visuals};

mod fonts;
mod text;
mod visuals;

pub fn load_fonts(ctx: &egui::Context) {
    // Load and set the fonts
    fonts::set(ctx);

    // Set the text styles
    ctx.style_mut(|style| {
        style.text_styles = text::styles();
    });
}

pub fn set_theme(ctx: &egui::Context, theme: egui::Theme) {
    // Set the style
    ctx.set_visuals(match theme {
        egui::Theme::Dark => dark_visuals().clone(),
        egui::Theme::Light => light_visuals().clone(),
    });
}
