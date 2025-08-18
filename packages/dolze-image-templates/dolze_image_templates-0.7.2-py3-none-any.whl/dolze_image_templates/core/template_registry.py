from typing import Dict, Any, Optional, List
import os
import json
import re
from pathlib import Path
from PIL import Image

from dolze_image_templates.core.template_engine import Template
from dolze_image_templates.core.font_manager import get_font_manager
from dolze_image_templates.core.template_samples import get_sample_url


class TemplateRegistry:
    """
    Registry for managing and accessing all available templates.
    Acts as a single point of contact for template-related operations.
    """
    
    # Template form values mapping
    _template_form_values = {}

    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the template registry.

        Args:
            templates_dir: Directory containing template definition files
        """
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.templates_dir = templates_dir or os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates"
        )
        self._load_templates()
        self._initialize_form_values()

    def _load_templates(self) -> None:
        """Load all templates from the templates directory."""
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir, exist_ok=True)
            return

        # Load all JSON files in the templates directory
        for file_path in Path(self.templates_dir).glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    template_data = json.load(f)
                    if isinstance(template_data, dict) and "name" in template_data:
                        self.templates[template_data["name"]] = template_data
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading template from {file_path}: {e}")

    def _has_image_upload(self, config: Any) -> bool:
        """Check if the template configuration contains any image upload fields.

        Args:
            config: Template configuration or part of it

        Returns:
            bool: True if any field value is "${image_url}", False otherwise
        """
        if isinstance(config, str):
            return config == "${image_url}"

        if not isinstance(config, (dict, list)):
            return False

        if isinstance(config, dict):
            for value in config.values():
                if value == "${image_url}":
                    return True
                if isinstance(value, (dict, list)) and self._has_image_upload(value):
                    return True
        elif isinstance(config, list):
            for item in config:
                if item == "${image_url}":
                    return True
                if isinstance(item, (dict, list)) and self._has_image_upload(item):
                    return True

        return False

    def get_all_templates(self) -> List[Dict[str, Any]]:
        """
        Get information about all available templates.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries containing template information with keys:
                - template_name: str - Name of the template
                - isImageUploadPresent: bool - True if template contains any image upload fields
                - sample_url: str - Placeholder for future sample URL (currently empty string)
        """
        # Initialize form values if not already done
        if not self._template_form_values:
            self._initialize_form_values()
            
        return [
    {
        "template_name": "calendar_app_promo",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('calendar_app_promo')
    },
    {
        "template_name": "testimonials_template",
        "isImageUploadPresent": False,
        "sample_url": get_sample_url('testimonials_template')
    },
    {
        "template_name": "coming_soon_post_2",
        "isImageUploadPresent": False,
        "sample_url": get_sample_url('coming_soon_post_2')
    },
    {
        "template_name": "blog_post",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('blog_post')
    },
    {
        "template_name": "blog_post_2",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('blog_post_2')
    },
    {
        "template_name": "qa_template",
        "isImageUploadPresent": False,
        "sample_url": get_sample_url('qa_template')
    },
    {
        "template_name": "qa_template_2",
        "isImageUploadPresent": False,
        "sample_url": get_sample_url('qa_template_2')
    },
    {
        "template_name": "quote_template",
        "isImageUploadPresent": False,
        "sample_url": get_sample_url('quote_template')
    },
    {
        "template_name": "quote_template_2",
        "isImageUploadPresent": False,
        "sample_url": get_sample_url('quote_template_2')
    },
    {
        "template_name": "education_info",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('education_info')
    },
    {
        "template_name": "education_info_2",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('education_info_2')
    },
    {
        "template_name": "product_promotion",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('product_promotion')
    },
    {
        "template_name": "product_promotion_2",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('product_promotion_2')
    },
    {
        "template_name": "product_showcase",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('product_showcase')
    },
    {
        "template_name": "product_showcase_2",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('product_showcase_2')
    },
    {
        "template_name": "coming_soon_page",
        "isImageUploadPresent": False,
        "sample_url": get_sample_url('coming_soon_page')
    },
    {
        "template_name": "product_showcase_3",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('product_showcase_3')
    },
    {
        "template_name": "coming_soon",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('coming_soon')
    },
    {
        "template_name": "event_day",
        "isImageUploadPresent": False,
        "sample_url": get_sample_url('event_day')
    },
    {
        "template_name": "hiring_post",
        "isImageUploadPresent": False,
        "sample_url": get_sample_url('hiring_post')
    },
    {
        "template_name": "product_sale",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('product_sale')
    },
    {
        "template_name": "product_service_minimal",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('product_service_minimal')
    },
    {
        "template_name": "product_showcase_4",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('product_showcase_4')
    },
    {
        "template_name": "summer_sale_promotion",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('summer_sale_promotion')
    },
    {
        "template_name": "testimonials_template_2",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('testimonials_template_2')
    },
    {
        "template_name": "product_showcase_5",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('product_showcase_5')
    },
    {
        "template_name": "brand_info",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('brand_info')
    },
    {
        "template_name": "product_marketing",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('product_marketing')
    },
    {
        "template_name": "brand_info_2",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('brand_info_2')
    },
    {
        "template_name": "product_sale_2",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('product_sale_2')
    },
    {
        "template_name": "product_feature",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('product_feature')
    },
    {
        "template_name": "event_alert",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('event_alert')
    },
    {
        "template_name": "sale_alert",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('sale_alert')
    },
    {
        "template_name": "testimonials",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('testimonials')
    },
    {
        "template_name": "event_announcement",
        "isImageUploadPresent": True,
        "sample_url": get_sample_url('event_announcement')
    }
]

    def register_template(self, name: str, config: Dict[str, Any]) -> None:
        """
        Register a new template.

        Args:
            name: Name of the template
            config: Template configuration dictionary
        """
        if not name:
            raise ValueError("Template name cannot be empty")

        # Ensure required fields are present
        required_fields = ["components"]
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Template config is missing required field: {field}")

        # Set default values
        config.setdefault("name", name)
        config.setdefault("size", {"width": 1080, "height": 1080})
        config.setdefault("background_color", [255, 255, 255])
        config.setdefault("use_base_image", False)

        self.templates[name] = config

        # Save to file
        self._save_template(name, config)

    def _save_template(self, name: str, config: Dict[str, Any]) -> None:
        """
        Save a template to a JSON file.

        Args:
            name: Name of the template
            config: Template configuration
        """
        try:
            os.makedirs(self.templates_dir, exist_ok=True)
            file_path = os.path.join(self.templates_dir, f"{name}.json")
            with open(file_path, "w") as f:
                json.dump(config, f, indent=2)
        except IOError as e:
            print(f"Error saving template {name}: {e}")

    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get a template configuration by name.

        Args:
            name: Name of the template

        Returns:
            Template configuration dictionary or None if not found
        """
        return self.templates.get(name)
        
    def get_template_form_values(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get form values for a specific template by name.
        
        Args:
            template_name: Name of the template to get form values for
            
        Returns:
            Dictionary of form values or None if not found
        """
        return self._template_form_values.get(template_name)
        
    def _initialize_form_values(self) -> None:
        """
        Initialize the form values mapping for all templates.
        This separates the form values from the template configurations.
        """
        # Clear existing form values
        self._template_form_values = {
   
    "cookie_poster": {
        "background_image_url": { "field": "background_image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "logo_url": { "field": "logo_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "headline": { "field": "headline", "type": "text", "minLength": 1, "maxLength": 50 },
        "subtitle": { "field": "subtitle", "type": "text", "minLength": 1, "maxLength": 100 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 20 },
        "cookie_image_url": { "field": "cookie_image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "samples": {
            "background_image_url": "https://example.com/blue_background.jpg",
            "logo_url": "https://example.com/bakery_logo.png",
            "headline": "Fresh Baked Cookies",
            "subtitle": "Made with premium ingredients daily",
            "theme_color": "#FF9900",
            "cta_text": "Order Now",
            "cookie_image_url": "https://example.com/chocolate_chip_cookies.png"
        },
        "fieldPrompt": {
            "background_image_url": "Generate a prompt for a blue bakery-themed background",
            "logo_url": "Bakery logo image",
            "headline": "A catchy headline for cookie promotion",
            "subtitle": "A brief description of the cookies",
            "theme_color": "#FF9900",
            "cta_text": "Call to action text",
            "cookie_image_url": "Generate a prompt for an appetizing cookie image"
        }
    },
    "juice_poster": {
        "background_image_url": { "field": "background_image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "logo_url": { "field": "logo_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "headline": { "field": "headline", "type": "text", "minLength": 1, "maxLength": 50 },
        "subtitle": { "field": "subtitle", "type": "text", "minLength": 1, "maxLength": 100 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 20 },
        "juice_image_url": { "field": "juice_image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "samples": {
            "background_image_url": "https://example.com/fruit_background.jpg",
            "logo_url": "https://example.com/juice_logo.png",
            "headline": "Fresh Squeezed Juice",
            "subtitle": "100% Natural, No Added Sugar",
            "theme_color": "#4CAF50",
            "cta_text": "Try Now",
            "juice_image_url": "https://example.com/orange_juice.png"
        },
        "fieldPrompt": {
            "background_image_url": "Generate a prompt for a vibrant fruit-themed background",
            "logo_url": "Juice brand logo image",
            "headline": "A catchy headline for juice promotion",
            "subtitle": "A brief description of the juice benefits",
            "theme_color": "#4CAF50",
            "cta_text": "Call to action text",
            "juice_image_url": "Generate a prompt for a refreshing juice image"
        }
    },
    "juice_poster_gif": {
        "background_image_url": { "field": "background_image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "logo_url": { "field": "logo_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "headline": { "field": "headline", "type": "text", "minLength": 1, "maxLength": 50 },
        "subtitle": { "field": "subtitle", "type": "text", "minLength": 1, "maxLength": 100 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 20 },
        "juice_image_url": { "field": "juice_image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "samples": {
            "background_image_url": "https://example.com/fruit_background.jpg",
            "logo_url": "https://example.com/juice_logo.png",
            "headline": "Fresh Squeezed Juice",
            "subtitle": "100% Natural, No Added Sugar",
            "theme_color": "#4CAF50",
            "cta_text": "Try Now",
            "juice_image_url": "https://example.com/orange_juice.png"
        },
        "fieldPrompt": {
            "background_image_url": "Generate a prompt for a vibrant fruit-themed background",
            "logo_url": "Juice brand logo image",
            "headline": "A catchy headline for juice promotion",
            "subtitle": "A brief description of the juice benefits",
            "theme_color": "#4CAF50",
            "cta_text": "Call to action text",
            "juice_image_url": "Generate a prompt for a refreshing juice image"
        }
    },
    "grilled_chicken_template": {
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000 },
        "product_name": { "field": "product_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "product_description": { "field": "product_description", "type": "text", "minLength": 1, "maxLength": 200 },
        "price": { "field": "price", "type": "text", "minLength": 1, "maxLength": 20 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "samples": {
            "product_image": "https://example.com/grilled_chicken.jpg",
            "product_name": "Grilled Chicken Platter",
            "product_description": "Tender grilled chicken served with fresh vegetables and homemade sauce",
            "price": "₹299",
            "theme_color": "#D32F2F"
        },
        "fieldPrompt": {
            "product_image": "Generate a prompt for an appetizing grilled chicken dish image",
            "product_name": "Name of the chicken dish",
            "product_description": "Description of the chicken dish and its ingredients",
            "price": "Price in INR",
            "theme_color": "#D32F2F"
        }
    },
    "healthy_food_template": {
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000 },
        "product_name": { "field": "product_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "product_description": { "field": "product_description", "type": "text", "minLength": 1, "maxLength": 200 },
        "price": { "field": "price", "type": "text", "minLength": 1, "maxLength": 20 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "samples": {
            "product_image": "https://example.com/healthy_salad.jpg",
            "product_name": "Superfood Salad Bowl",
            "product_description": "Fresh mixed greens with quinoa, avocado, and nutrient-rich toppings",
            "price": "₹249",
            "theme_color": "#43A047"
        },
        "fieldPrompt": {
            "product_image": "Generate a prompt for a vibrant healthy food image",
            "product_name": "Name of the healthy dish",
            "product_description": "Description of the healthy dish and its nutritional benefits",
            "price": "Price in INR",
            "theme_color": "#43A047"
        }
    },
    "learn_gif_template": {
        "heading": { "field": "heading", "type": "text", "minLength": 1, "maxLength": 50 },
        "subheading": { "field": "subheading", "type": "text", "minLength": 1, "maxLength": 100 },
        "background_color": { "field": "background_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "image_url": { "field": "image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "samples": {
            "heading": "Learn Something New",
            "subheading": "Expand your knowledge with our interactive courses",
            "background_color": "#6200EA",
            "image_url": "https://example.com/learning_illustration.png"
        },
        "fieldPrompt": {
            "heading": "A catchy educational heading",
            "subheading": "A brief description of the learning content",
            "background_color": "#6200EA",
            "image_url": "Generate a prompt for an educational illustration image"
        }
    },
    
    "orchid_baby_post": {
        "image_url": { "field": "image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "heading": { "field": "heading", "type": "text", "minLength": 1, "maxLength": 50 },
        "subheading": { "field": "subheading", "type": "text", "minLength": 1, "maxLength": 100 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "samples": {
            "image_url": "https://example.com/baby_products.jpg",
            "heading": "Baby Care Essentials",
            "subheading": "Gentle and safe products for your little one",
            "theme_color": "#EC407A"
        },
        "fieldPrompt": {
            "image_url": "Generate a prompt for a baby care product image",
            "heading": "A short heading for baby products",
            "subheading": "A brief description of baby care products",
            "theme_color": "#EC407A"
        }
    },
    "shelf_engine_template": {
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000 },
        "product_name": { "field": "product_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "product_description": { "field": "product_description", "type": "text", "minLength": 1, "maxLength": 200 },
        "price": { "field": "price", "type": "text", "minLength": 1, "maxLength": 20 },
        "discount": { "field": "discount", "type": "text", "minLength": 1, "maxLength": 10 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "samples": {
            "product_image": "https://example.com/engine_product.jpg",
            "product_name": "High-Performance Engine",
            "product_description": "Advanced automotive engine with superior fuel efficiency and power output",
            "price": "$1,299",
            "discount": "15% OFF",
            "theme_color": "#F57C00"
        },
        "fieldPrompt": {
            "product_image": "Generate a prompt for an engine or mechanical part image",
            "product_name": "Name of the engine or mechanical product",
            "product_description": "Description of the product features and benefits",
            "price": "Price with currency symbol",
            "discount": "Discount percentage",
            "theme_color": "#F57C00"
        }
    },
    "shoe_ad_template": {
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000 },
        "product_name": { "field": "product_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "product_description": { "field": "product_description", "type": "text", "minLength": 1, "maxLength": 200 },
        "price": { "field": "price", "type": "text", "minLength": 1, "maxLength": 20 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 20 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "samples": {
            "product_image": "https://example.com/running_shoes.jpg",
            "product_name": "UltraBoost Running Shoes",
            "product_description": "Lightweight and responsive running shoes with superior cushioning for maximum comfort",
            "price": "$129.99",
            "cta_text": "Shop Now",
            "theme_color": "#00BCD4"
        },
        "fieldPrompt": {
            "product_image": "Generate a prompt for a shoe product image",
            "product_name": "Name of the shoe product",
            "product_description": "Description of the shoe features and benefits",
            "price": "Price with currency symbol",
            "cta_text": "Call to action text",
            "theme_color": "#00BCD4"
        }
    },
    "stamped_loyalty_template": {
        "logo_url": { "field": "logo_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "heading": { "field": "heading", "type": "text", "minLength": 1, "maxLength": 50 },
        "subheading": { "field": "subheading", "type": "text", "minLength": 1, "maxLength": 100 },
        "points": { "field": "points", "type": "text", "minLength": 1, "maxLength": 10 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 20 },
        "samples": {
            "logo_url": "https://example.com/cafe_logo.png",
            "heading": "Loyalty Rewards",
            "subheading": "Earn points with every purchase",
            "points": "250",
            "theme_color": "#795548",
            "cta_text": "Redeem Now"
        },
        "fieldPrompt": {
            "logo_url": "Business logo image",
            "heading": "Loyalty program name",
            "subheading": "Brief description of the loyalty program",
            "points": "Number of points earned",
            "theme_color": "#795548",
            "cta_text": "Call to action text"
        }
    },
    "status_indicator": {
        "status_text": { "field": "status_text", "type": "text", "minLength": 1, "maxLength": 50 },
        "status_color": { "field": "status_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "description": { "field": "description", "type": "text", "minLength": 1, "maxLength": 200 },
        "samples": {
            "status_text": "In Progress",
            "status_color": "#FFC107",
            "description": "Your order is being processed and will be shipped soon"
        },
        "fieldPrompt": {
            "status_text": "Status label text",
            "status_color": "Color code for status indicator",
            "description": "Detailed description of the status"
        }
    },
    "super_king_burgers_template": {
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000 },
        "product_name": { "field": "product_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "product_description": { "field": "product_description", "type": "text", "minLength": 1, "maxLength": 200 },
        "price": { "field": "price", "type": "text", "minLength": 1, "maxLength": 20 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "samples": {
            "product_image": "https://example.com/king_burger.jpg",
            "product_name": "Super King Burger",
            "product_description": "Triple patty burger with cheese, bacon, and our special sauce",
            "price": "$12.99",
            "theme_color": "#D84315"
        },
        "fieldPrompt": {
            "product_image": "Generate a prompt for an appetizing burger image",
            "product_name": "Name of the burger",
            "product_description": "Description of the burger ingredients",
            "price": "Price with currency symbol",
            "theme_color": "#D84315"
        }
    },
    "testing_template": {
        "heading": { "field": "heading", "type": "text", "minLength": 1, "maxLength": 50 },
        "subheading": { "field": "subheading", "type": "text", "minLength": 1, "maxLength": 100 },
        "image_url": { "field": "image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "samples": {
            "heading": "Test Template",
            "subheading": "This is a template for testing purposes",
            "image_url": "https://example.com/test_image.jpg"
        },
        "fieldPrompt": {
            "heading": "A test heading",
            "subheading": "A test subheading",
            "image_url": "Generate a prompt for a test image"
        }
    },
    "calendar_app_promo": {
        "image_url": { "field": "image_url", "type": "image", "minLength": 0, "maxLength": 1000, "isTransparentImage": True },
        "heading": { "field": "heading", "type": "text", "minLength": 1, "maxLength": 50 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 20 },
        "subheading": { "field": "subheading", "type": "text", "minLength": 1, "maxLength": 100 },
        "samples": {
            "image_url": "https://example.com/product_calendar.png",
            "heading": "Plan your day in a snap",
            "cta_text": "Get Started",
            "subheading": "Organize your schedule effortlessly with our intuitive app."
        },
        "fieldPrompt": {
            "image_url": "Generate a prompt for product image which has transparent background as a png image. Make sure just the product is visible and the background is transparent. Also dont keep any text in the image. Make sure it has transparent background makes sure it has transparent background (alpha PNG) and also has isolated object cut-out Isolated object cut-out on a completely transparent background (alpha PNG). No floor, no shadows, no reflections, no props, no text—only the product, perfectly lit",
            "heading": "Plan your day in a snap"
        }
    },
    "testimonials_template": {
        "user_name": { "field": "user_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "user_title": { "field": "user_title", "type": "text", "minLength": 1, "maxLength": 100 },
        "testimonial_text": { "field": "testimonial_text", "type": "text", "minLength": 1, "maxLength": 189 },
        "samples": {
            "user_name": "Sarah Johnson",
            "user_title": "Verified Buyer",
            "testimonial_text": "This product has transformed how we work daily."
        },
        "fieldPrompt": {
            "user_name": "Sarah Johnson",
            "user_title": "Verified Buyer",
            "testimonial_text": "This product has transformed how we work in under 27 words"
        }
    },
    "coming_soon_post_2": {
        "text": { "field": "text", "type": "text", "minLength": 50, "maxLength": 84 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 15, "maxLength": 28 },
        "samples": {
            "text": "Our new product launches in just a few days! Stay tuned!",
            "cta_text": "Join the Waitlist Now"
        },
        "fieldPrompt": {
            "text": "a text in 10-12 words telling users that one of thier new product will be launch in few days",
            "cta_text": "A Good cta text in 3-4 words"
        }
    },
    "blog_post": {
        "title": { "field": "title", "type": "text", "minLength": 1, "maxLength": 100 },
        "author": { "field": "author", "type": "text", "minLength": 1, "maxLength": 50 },
        "read_time": { "field": "read_time", "type": "number", "minLength": 1, "maxLength": 3 },
        "image_url": { "field": "image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "website_url": { "field": "website_url", "type": "url", "minLength": 1, "maxLength": 200 },
        "publish_date": { "field": "publish_date", "type": "text", "minLength": 10, "maxLength": 10 },
        "excerpt": { "field": "excerpt", "type": "text", "minLength": 1, "maxLength": 200 },
        "samples": {
            "title": "How to be environment conscious without being weird",
            "author": "@username",
            "read_time": 4,
            "image_url": "https://example.com/eco_scene.jpg",
            "website_url": "example.com",
            "publish_date": "2025-06-22",
            "excerpt": "Learn eco-friendly habits that fit seamlessly into your daily life."
        },
        "fieldPrompt": {
            "title": "How to be environment conscious without being weird",
            "author": "@username",
            "read_time": "4",
            "image_url": "Generate a prompt for an image of an eco-friendly scene with sustainable practices like recycling, solar panels, and greenery, in a bright, inviting style",
            "website_url": "example.com",
            "publish_date": "2025-06-22",
            "excerpt": "This is a short description of the blog post. This will be used to display the blog post in the feed."
        }
    },
    "blog_post_2": {
        "title": { "field": "title", "type": "text", "minLength": 1, "maxLength": 100 },
        "author": { "field": "author", "type": "text", "minLength": 1, "maxLength": 50 },
        "read_time": { "field": "read_time", "type": "number", "minLength": 1, "maxLength": 3 },
        "image_url": { "field": "image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "publish_date": { "field": "publish_date", "type": "text", "minLength": 10, "maxLength": 10 },
        "excerpt": { "field": "excerpt", "type": "text", "minLength": 1, "maxLength": 200 },
        "samples": {
            "title": "How to be environment conscious without being weird",
            "author": "@username",
            "read_time": 4,
            "image_url": "https://example.com/green_living.jpg",
            "publish_date": "2025-06-22",
            "excerpt": "Discover sustainable practices for a modern eco-friendly lifestyle."
        },
        "fieldPrompt": {
            "title": "How to be environment conscious without being weird",
            "author": "@username",
            "read_time": "4",
            "image_url": "Generate a prompt for a vibrant image of green living practices, featuring reusable items, plants, and a modern eco-home, in a clean, aesthetic style",
            "publish_date": "2025-06-22",
            "excerpt": "This si a short description of the blog post. this is to be inserted by db and will be used to display the blog post in the feed"
        }
    },
    "qa_template": {
        "question": { "field": "question", "type": "text", "minLength": 1, "maxLength": 28 },
        "answer": { "field": "answer", "type": "text", "minLength": 1, "maxLength": 200 },
        "username": { "field": "username", "type": "text", "minLength": 1, "maxLength": 50 },
        "website_url": { "field": "website_url", "type": "url", "minLength": 1, "maxLength": 200 },
        "samples": {
            "question": "What is renewable energy?",
            "answer": "One wind turbine can power 1,500 homes annually!",
            "username": "@username",
            "website_url": "example.com"
        },
        "fieldPrompt": {
            "question": "A question in under 3-4 words",
            "answer": "One wind turbine can produce enough electricity to power around 1,500 homes annually!",
            "username": "@username"
        }
    },
    "qa_template_2": {
        "question": { "field": "question", "type": "text", "minLength": 1, "maxLength": 28 },
        "answer": { "field": "answer", "type": "text", "minLength": 150, "maxLength": 280 },
        "username": { "field": "username", "type": "text", "minLength": 1, "maxLength": 50 },
        "website_url": { "field": "website_url", "type": "url", "minLength": 1, "maxLength": 200 },
        "samples": {
            "question": "How do turbines work?",
            "answer": "Wind turbines convert wind energy into electricity using blades that spin a generator, producing clean power for approximately 1,500 homes annually with minimal environmental impact.",
            "username": "@username",
            "website_url": "example.com"
        },
        "fieldPrompt": {
            "question": "a question in under 3-4 words",
            "answer": "a 30-40 words answer for the above question",
            "username": "@username"
        }
    },
    "quote_template": {
        "quote": { "field": "quote", "type": "text", "minLength": 70, "maxLength": 126 },
        "username": { "field": "username", "type": "text", "minLength": 1, "maxLength": 50 },
        "samples": {
            "quote": "Success is not the absence of obstacles, but the courage to push through them.",
            "username": "@motivator"
        },
        "fieldPrompt": {
            "quote": "a quote for the wbesite in around 14-18 words"
        }
    },
    "quote_template_2": {
        "quote1": { "field": "quote1", "type": "text", "minLength": 175, "maxLength": 280 },
        "quote2": { "field": "quote2", "type": "text", "minLength": 1, "maxLength": 200 },
        "username": { "field": "username", "type": "text", "minLength": 1, "maxLength": 50 },
        "samples": {
            "quote1": "Our innovative solutions streamline your workflow, saving time and boosting productivity across industries with cutting-edge technology.",
            "quote2": "Empowering businesses to thrive.",
            "username": "@stevejobs"
        },
        "fieldPrompt": {
            "quote1": "genereate a phrase in about 35-40 words about this business/problem its solving or the industry it operates in",
            "username": "@stevejobs"
        }
    },
    "education_info": {
        "product_info": { "field": "product_info", "type": "text", "minLength": 1, "maxLength": 600 },
        "product_name": { "field": "product_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "author": { "field": "author", "type": "text", "minLength": 1, "maxLength": 50 },
        "read_time": { "field": "read_time", "type": "number", "minLength": 1, "maxLength": 3 },
        "image_url": { "field": "image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "samples": {
            "product_info": "Our company harnesses wind energy to power 1,500 homes per turbine annually.",
            "product_name": "EcoWind",
            "author": "@username",
            "read_time": 4,
            "image_url": "https://example.com/wind_turbine.jpg"
        },
        "fieldPrompt": {
            "product_info": "Write a brief text in under 600 chars which is a fact related to company or domain they operate in",
            "product_name": "Product Name",
            "author": "@username",
            "read_time": "4",
            "image_url": "Generate a prompt for an image of a wind turbine in a scenic landscape with clear skies and rolling hills, in a realistic style"
        }
    },
    "education_info_2": {
        "product_info": { "field": "product_info", "type": "text", "minLength": 1, "maxLength": 300 },
        "author": { "field": "author", "type": "text", "minLength": 1, "maxLength": 50 },
        "read_time": { "field": "read_time", "type": "number", "minLength": 1, "maxLength": 3 },
        "image_url": { "field": "image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "samples": {
            "product_info": "How do wind turbines work? They convert wind into electricity efficiently.",
            "author": "@username",
            "read_time": 4,
            "image_url": "https://example.com/clean_energy.jpg"
        },
        "fieldPrompt": {
            "product_info": "a faq regarding the product or company or the domain they operate in, in under 300 chars",
            "author": "@username",
            "read_time": "4",
            "image_url": "Generate a prompt for an image of a clean energy scene with multiple wind turbines in a modern, eco-friendly landscape"
        }
    },
    "product_promotion": {
        "image_url": { "field": "image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "heading": { "field": "heading", "type": "text", "minLength": 1, "maxLength": 21 },
        "subheading": { "field": "subheading", "type": "text", "minLength": 150, "maxLength": 280 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 14 },
        "website_url": { "field": "website_url", "type": "url", "minLength": 1, "maxLength": 14 },
        "logo_url": { "field": "logo_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "samples": {
            "image_url": "https://example.com/product_promo.jpg",
            "heading": "Smart Planner",
            "subheading": "Boost productivity with our intuitive planner designed for seamless organization and efficient task management across all your devices.",
            "cta_text": "Shop Now",
            "website_url": "dolze.ai",
            "logo_url": "https://example.com/logo.png"
        },
        "fieldPrompt": {
            "image_url": "Generate a prompt for a visually appealing portrait image of the product. The image should be in a clean, modern style and in portrait format",
            "heading": "a simple 2-3 word heading related to the product",
            "subheading": "a simple 30-40 word subheading related to the product",
            "cta_text": "a simple 1-2 word CTA text related to the product",
            "website_url": "a simple 1-2 word website url related to the product"
        }
    },
    "product_promotion_2": {
        "image_url": { "field": "image_url", "type": "image", "minLength": 0, "maxLength": 1000, "isTransparentImage": True },
        "quote1": { "field": "quote1", "type": "text", "minLength": 15, "maxLength": 28 },
        "quote2": { "field": "quote2", "type": "text", "minLength": 1, "maxLength": 50 },
        "samples": {
            "image_url": "https://example.com/kanban_board.png",
            "quote1": "Organize with Ease",
            "quote2": "Streamline your workflow today"
        },
        "fieldPrompt": {
            "image_url": "Generate a prompt for a visually appealing image of a kanban board interface with colorful task cards and a modern, user-friendly layout",
            "quote1": "the first line of quote in 3-4 words to be shown in white color",
            "quote2": "the continued quote to be shown in next line for few words"
        }
    },
    "product_showcase": {
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000 },
        "product_name": { "field": "product_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "product_price": { "field": "product_price", "type": "text", "minLength": 1, "maxLength": 20 },
        "product_description": { "field": "product_description", "type": "text", "minLength": 1, "maxLength": 100 },
        "badge_text": { "field": "badge_text", "type": "text", "minLength": 1, "maxLength": 20 },
        "samples": {
            "product_image": "https://example.com/product.jpg",
            "product_name": "Eco Planner",
            "product_price": "₹2999",
            "product_description": "Sustainable planner for organized living",
            "badge_text": "Bestseller"
        },
        "fieldPrompt": {
            "product_image": "Generate a prompt for a high-quality image for this product based on context you have",
            "product_name": "Product Name",
            "product_price": "a price for this product in INR",
            "product_description": "crisp and brief product description in under 100 chars",
            "badge_text": "Bestseller"
        }
    },
    "product_showcase_2": {
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000 },
        "product_name": { "field": "product_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "product_price": { "field": "product_price", "type": "text", "minLength": 1, "maxLength": 20 },
        "product_description": { "field": "product_description", "type": "text", "minLength": 90, "maxLength": 147 },
        "badge_text": { "field": "badge_text", "type": "text", "minLength": 10, "maxLength": 10 },
        "samples": {
            "product_image": "https://example.com/product2.jpg",
            "product_name": "Eco Planner",
            "product_price": "₹2999",
            "product_description": "Eco-friendly planner with reusable pages for sustainable organization",
            "badge_text": "Bestseller"
        },
        "fieldPrompt": {
            "product_image": "Generate a prompt for a high-quality image for this product based on context you have",
            "product_name": "Product Name",
            "product_price": "a price for this product in INR",
            "product_description": "Detailed product description in aroudn 18-21 words",
            "badge_text": "Bestseller, Dont change it keep it bestseller always"
        }
    },
    "coming_soon_page": {
        "header_text": { "field": "header_text", "type": "text", "minLength": 1, "maxLength": 21 },
        "contact_email": { "field": "contact_email", "type": "email", "minLength": 5, "maxLength": 100 },
        "website_url": { "field": "website_url", "type": "url", "minLength": 1, "maxLength": 200 },
        "contact_details": { "field": "contact_details", "type": "text", "minLength": 1, "maxLength": 200 },
        "samples": {
            "header_text": "Launch Soon",
            "contact_email": "info@dolze.ai",
            "website_url": "dolze.ai",
            "contact_details": "Reach out at info@dolze.ai for updates."
        },
        "fieldPrompt": {
            "header_text": "a 2-3 word text for the coming soon page which would be placed above the coming soon text in the coming soon post for social media",
            "contact_email": "contact email"
        }
    },
    "product_showcase_3": {
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000, "isTransparentImage": True },
        "product_name": { "field": "product_name", "type": "text", "minLength": 1, "maxLength": 21 },
        "product_price": { "field": "product_price", "type": "text", "minLength": 1, "maxLength": 20 },
        "product_description": { "field": "product_description", "type": "text", "minLength": 30, "maxLength": 49 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 14 },
        "samples": {
            "product_image": "https://example.com/product3.png",
            "product_name": "Smart Widget",
            "product_price": "$99.99",
            "product_description": "Innovative widget for seamless productivity",
            "cta_text": "Book Now"
        },
        "fieldPrompt": {
            "product_image": "Generate a prompt for product image which has transparent background as a png image. Make sure just the product is visible and the background is transparent. Also dont keep any text in the image. Make sure it has transparent background makes sure it has transparent background (alpha PNG) and also has isolated object cut-out Isolated object cut-out on a completely transparent background (alpha PNG). No floor, no shadows, no reflections, no props, no text—only the product, perfectly lit",
            "product_name": "Product Name in under 2-3 words",
            "product_price": "$99.99",
            "product_description": "Detailed product description in 6-7 words",
            "cta_text": "book now / get started or somethign similar in 2 words"
        }
    },
    "coming_soon": {
        "background_image_url": { "field": "background_image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "business_name": { "field": "business_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "text": { "field": "text", "type": "text", "minLength": 1, "maxLength": 21 },
        "website_url": { "field": "website_url", "type": "url", "minLength": 1, "maxLength": 200 },
        "heading": { "field": "heading", "type": "text", "minLength": 1, "maxLength": 50 },
        "subheading": { "field": "subheading", "type": "text", "minLength": 1, "maxLength": 100 },
        "samples": {
            "background_image_url": "https://example.com/coming_soon_bg.jpg",
            "business_name": "Dolze AI",
            "text": "Notify Me",
            "website_url": "dolze.ai",
            "heading": "New Product Coming",
            "subheading": "Revolutionary tool launching soon!"
        },
        "fieldPrompt": {
            "background_image_url": "Generate a prompt for 1080 * 1080 backgroung image related to product/ service which can be used as a background image",
            "business_name": "business name",
            "text": "Notify Me or something similar in 2-3 words",
            "website_url": "website_url"
        }
    },
    "event_day": {
        "celebration_name": { "field": "celebration_name", "type": "text", "minLength": 1, "maxLength": 21 },
        "celebration_text": { "field": "celebration_text", "type": "text", "minLength": 1, "maxLength": 21 },
        "celebration_description": { "field": "celebration_description", "type": "text", "minLength": 40, "maxLength": 70 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "samples": {
            "celebration_name": "Eco Fest",
            "celebration_text": "Green Day",
            "celebration_description": "Join us for a special eco-friendly celebration event!",
            "theme_color": "#FF5733"
        },
        "fieldPrompt": {
            "celebration_name": "Event Name in 2-3 words",
            "celebration_text": "Special Day in 2-3 words",
            "celebration_description": "Join us for a special celebration or something similar in 8-10 words",
            "theme_color": "#FF5733"
        }
    },
    "hiring_post": {
        "heading": { "field": "heading", "type": "text", "minLength": 1, "maxLength": 21 },
        "subheading": { "field": "subheading", "type": "text", "minLength": 1, "maxLength": 100 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 14 },
        "job_title": { "field": "job_title", "type": "text", "minLength": 1, "maxLength": 21 },
        "company_name": { "field": "company_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "samples": {
            "heading": "We're Hiring!",
            "subheading": "Join our amazing team. We're looking for talented individuals.",
            "theme_color": "#7d00eb",
            "cta_text": "Apply Now",
            "job_title": "Software Engineer",
            "company_name": "Dolze AI"
        },
        "fieldPrompt": {
            "heading": "We're Hiring! or somethign similar in under 2-3 words",
            "subheading": "Join our amazing team. We're looking for talented individuals.",
            "theme_color": "#7d00eb",
            "cta_text": "cta text in under 1-2 words",
            "job_title": "in under 2-3 words",
            "company_name": "name of company"
        }
    },
    "product_sale": {
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 14 },
        "sale_end_text": { "field": "sale_end_text", "type": "text", "minLength": 1, "maxLength": 20 },
        "product_name": { "field": "product_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "product_description": { "field": "product_description", "type": "text", "minLength": 20, "maxLength": 35 },
        "sale_heading": { "field": "sale_heading", "type": "text", "minLength": 1, "maxLength": 21 },
        "sale_text": { "field": "sale_text", "type": "text", "minLength": 15, "maxLength": 28 },
        "background_image_url": { "field": "background_image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000, "isTransparentImage": True },
        "samples": {
            "cta_text": "Shop Now",
            "sale_end_text": "2025-08-31",
            "product_name": "Smart Gadget",
            "product_description": "Innovative tool for everyday solutions",
            "sale_heading": "50% OFF Sale",
            "sale_text": "Limited Time Offer",
            "background_image_url": "https://example.com/sale_bg.jpg",
            "theme_color": "#4A90E2",
            "product_image": "https://example.com/gadget.png"
        },
        "fieldPrompt": {
            "cta_text": "cta text in 1-2 words",
            "sale_end_text": "date at which sale ends",
            "product_name": "Product Name",
            "product_description": "Amazing product that solves your problems in under 4-5 words",
            "sale_heading": "flat 50% OFF in under 2-3 words",
            "sale_text": "Limited Time Offer or similar in under 3-4 words",
            "background_image_url": "Generate a prompt for an attractive product image on a clean background",
            "theme_color": "#4A90E2",
            "product_image": "a prompt for image of the product with transparent background just the product"
        }
    },
    "product_service_minimal": {
        "text": { "field": "text", "type": "text", "minLength": 40, "maxLength": 70 },
        "website_url": { "field": "website_url", "type": "url", "minLength": 1, "maxLength": 200 },
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "samples": {
            "text": "Streamlined service for efficient task management",
            "website_url": "example.com",
            "product_image": "https://example.com/minimal_product.jpg",
            "theme_color": "#FF5733"
        },
        "fieldPrompt": {
            "text": "Product/Service description in 8-10 words",
            "website_url": "example.com",
            "product_image": "Generate a prompt for a clean, minimal product image",
            "theme_color": "#FF5733"
        }
    },
    "product_showcase_4": {
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000, "isTransparentImage": True },
        "offer_text": { "field": "offer_text", "type": "text", "minLength": 1, "maxLength": 21 },
        "website_url": { "field": "website_url", "type": "url", "minLength": 1, "maxLength": 200 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "samples": {
            "product_image": "https://example.com/product4.png",
            "offer_text": "50% OFF",
            "website_url": "example.com/shop",
            "theme_color": "#4A90E2"
        },
        "fieldPrompt": {
            "product_image": "Generate a prompt for a professional product image which has transparent background as a png image. Make sure just the product is visible and the background is transparent. Also dont keep any text in the image. Make sure it has transparent background makes sure it has transparent background (alpha PNG) and also has isolated object cut-out Isolated object cut-out on a completely transparent background (alpha PNG). No floor, no shadows, no reflections, no props, no text—only the product, perfectly lit",
            "offer_text": "Special Offer\n50% OFF or something similar strictly in under 2-3 words",
            "website_url": "example.com/shop",
            "theme_color": "#4A90E2"
        }
    },
    "summer_sale_promotion": {
        "background_image_url": { "field": "background_image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "brand_name": { "field": "brand_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "sale_heading": { "field": "sale_heading", "type": "text", "minLength": 1, "maxLength": 50 },
        "sale_description": { "field": "sale_description", "type": "text", "minLength": 1, "maxLength": 56 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "discount_text": { "field": "discount_text", "type": "text", "minLength": 15, "maxLength": 28 },
        "social_handle": { "field": "social_handle", "type": "text", "minLength": 1, "maxLength": 50 },
        "contact_number": { "field": "contact_number", "type": "tel", "minLength": 10, "maxLength": 15 },
        "samples": {
            "background_image_url": "https://example.com/summer_sale_bg.jpg",
            "brand_name": "Dolze AI",
            "sale_heading": "SUMMER SALE",
            "sale_description": "Huge discounts this summer",
            "theme_color": "#FF6B6B",
            "discount_text": "Up to 50% off",
            "social_handle": "@dolze_ai",
            "contact_number": "+12345678901"
        },
        "fieldPrompt": {
            "background_image_url": "Generate a prompt to generate an image for a vibrant summer-themed background related to the product",
            "brand_name": "YOUR BRAND name",
            "sale_heading": "SUMMER SALE or similar",
            "sale_description": "A biref intro to the sale in under 7-8 words",
            "theme_color": "#FF6B6B",
            "discount_text": "upto 50% off or similar in under 3-4 words",
            "social_handle": "@dolze_ai",
            "contact_number": "random contact number"
        }
    },
    "testimonials_template_2": {
        "testimonial_text": { "field": "testimonial_text", "type": "text", "minLength": 20, "maxLength": 200 },
        "user_avatar": { "field": "user_avatar", "type": "image", "minLength": 0, "maxLength": 1000 },
        "user_name": { "field": "user_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "user_title": { "field": "user_title", "type": "text", "minLength": 1, "maxLength": 100 },
        "website_url": { "field": "website_url", "type": "url", "minLength": 1, "maxLength": 200 },
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "samples": {
            "testimonial_text": "This product transformed our workflow. Highly recommend it!",
            "user_avatar": "https://example.com/user_avatar.jpg",
            "user_name": "Jane Doe",
            "user_title": "CEO, TechCorp",
            "website_url": "dolze.ai/download",
            "theme_color": "#4A90E2"
        },
        "fieldPrompt": {
            "testimonial_text": "Share what customers are saying about your product/service (2-3 sentences)",
            "user_avatar": "URL to customer's profile picture mostly use some working stock images",
            "user_name": "Customer Name",
            "user_title": "Customer Title/Company",
            "website_url": "dolze.ai/download",
            "theme_color": "#4A90E2"
        }
    },
    "product_showcase_5": {
        "heading": { "field": "heading", "type": "text", "minLength": 1, "maxLength": 28 },
        "subheading": { "field": "subheading", "type": "text", "minLength": 1, "maxLength": 280 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 20 },
        "contact_number": { "field": "contact_number", "type": "tel", "minLength": 10, "maxLength": 15 },
        "website_url": { "field": "website_url", "type": "url", "minLength": 1, "maxLength": 200 },
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000, "isTransparentImage": True },
        "samples": {
            "heading": "Healthy Happy Living",
            "subheading": "Transform your lifestyle with our eco-friendly wellness products.",
            "cta_text": "Book Now",
            "contact_number": "+09876543211",
            "website_url": "dolze.ai",
            "product_image": "https://example.com/wellness_product.png"
        },
        "fieldPrompt": {
            "heading": "a heading like 'Healthy living happy living' in strictly under 4 words",
            "subheading": "a description in under 40 words",
            "cta_text": "Book Now",
            "contact_number": "+09876543211",
            "website_url": "dolze.ai",
            "product_image": "Generate a prompt for product image which has transparent background as a png image. Make sure just the product is visible and the background is transparent. Also dont keep any text in the image. Make sure it has transparent background makes sure it has transparent background (alpha PNG) and also has isolated object cut-out Isolated object cut-out on a completely transparent background (alpha PNG). No floor, no shadows, no reflections, no props, no text—only the product, perfectly lit"
        }
    },
    "brand_info": {
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000 },
        "heading": { "field": "heading", "type": "text", "minLength": 1, "maxLength": 35 },
        "subheading": { "field": "subheading", "type": "text", "minLength": 100, "maxLength": 175 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 10, "maxLength": 28 },
        "samples": {
            "product_image": "https://example.com/company_culture.jpg",
            "heading": "Our Team Spirit",
            "subheading": "We foster collaboration and innovation to build a thriving workplace culture.",
            "cta_text": "Join Our Team"
        },
        "fieldPrompt": {
            "product_image": "generate a prompt for a sqwuare image for background image of the post for a post showing things about comanpy culture and bonding",
            "heading": "a heading for the post in under 4-5 words",
            "subheading": "a subheading for the psot in under 20-25 words",
            "cta_text": "a cta for the text in 2-4 words"
        }
    },
    "product_marketing": {
        "social_handle": { "field": "social_handle", "type": "text", "minLength": 1, "maxLength": 50, "default": "@dolze.ai" },
        "heading": { "field": "heading", "type": "text", "minLength": 1, "maxLength": 26 },
        "subheading": { "field": "subheading", "type": "text", "minLength": 100, "maxLength": 175 },
        "background_image_url": { "field": "background_image_url", "type": "image", "minLength": 0, "maxLength": 1000 },
        "samples": {
            "social_handle": "@dolze.ai",
            "heading": "Boost Your Marketing",
            "subheading": "Elevate your brand with our innovative marketing tools and strategies.",
            "background_image_url": "https://example.com/marketing_bg.jpg"
        },
        "fieldPrompt": {
            "social_handle": "@dolze.ai",
            "heading": "Improve your business marketing or something similar in under 26-27 characters",
            "description": "a description matching the above headign in under 200 chars",
            "background_image_url": "a prompt for a bg image for the above idea. it should be a portrait image with aspect ratio of 1920 by 1080"
        }
    },
    "brand_info_2": {
        "service_hook": { "field": "service_hook", "type": "text", "minLength": 1, "maxLength": 23 },
        "content": { "field": "content", "type": "text", "minLength": 1, "maxLength": 50 },
        "contact_number": { "field": "contact_number", "type": "text", "minLength": 1, "maxLength": 12 },
        "website_url": { "field": "website_url", "type": "text", "minLength": 1, "maxLength": 35 },
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000 },
        "contact_email": { "field": "contact_email", "type": "text", "minLength": 1, "maxLength": 25 },
        "samples": {
            "service_hook": "Need a brand new",
            "content": "Expert developers deliver top-tier websites",
            "contact_number": "+123-456-7890",
            "website_url": "www.dolze.ai/careers",
            "product_image": "https://example.com/website_design.jpg",
            "contact_email": "contact@dolze.ai"
        },
        "fieldPrompt": {
            "service_hook": "A hook similar to 'do you need a brand new' or somethign similar in under 5-6 words, dont add the product name to any of them it will be added in the product_name field",
            "service_name": "The service name eg: 'website ?'. maek sure to add soemthing that completes the sentence in service_hook . keep it strictly under 12 characters",
            "content": "our team of expert devlopers will make sure you will get the best website available in the market",
            "contact_number": "+123-456-7890",
            "website_url": "www.dolze.ai/careers",
            "product_image": "a prompt for a produce image for the above idea. it should be a portrait image with aspect ratio of 1920 by 1080",
            "contact_email": "contact@dolze.ai"
        }
    },
    "product_sale_2": {
        "theme_color": { "field": "theme_color", "type": "text", "minLength": 4, "maxLength": 7 },
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000, "isTransparentImage": True },
        "heading": { "field": "heading", "type": "text", "minLength": 1, "maxLength": 26 },
        "usp1": { "field": "usp1", "type": "text", "minLength": 1, "maxLength": 16 },
        "usp2": { "field": "usp2", "type": "text", "minLength": 1, "maxLength": 16 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 10 },
        "product_highlights": { "field": "product_highlights", "type": "text", "minLength": 1, "maxLength": 14 },
        "social_handle": { "field": "social_handle", "type": "text", "minLength": 1, "maxLength": 25 },
        "business_name": { "field": "business_name", "type": "text", "minLength": 1, "maxLength": 25 },
        "samples": {
            "theme_color": "#4A90E2",
            "product_image": "https://images.pexels.com/photos/1181677/pexels-photo-1181677.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            "heading": "Digital Planner",
            "usp1": "Undated Planner",
            "usp2": "Hyperlinked Pages",
            "cta_text": "Book Now",
            "product_highlights": "Seamless Planning",
            "social_handle": "@dolze_ai",
            "business_name": "Dolze AI"
        },
        "fieldPrompt": {
            "product_image": "https://images.pexels.com/photos/1181677/pexels-photo-1181677.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
            "heading": "Digital planner or something similar in under 17 characters",
            "usp1": "Undated Planner or something similar in under 16 characters",
            "usp2": "Hyperlinked Pages or something similar in under 16 characters",
            "cta_text": "Book Now or something similar in under 10 characters",
            "product_highlights": "highlight of product in under 14 characters",
            "business_name": "name of the business"
        }
    },
    "product_feature": {
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000, "isTransparentImage": True },
        "feature1": { "field": "feature1", "type": "text", "minLength": 1, "maxLength": 50 },
        "feature2": { "field": "feature2", "type": "text", "minLength": 1, "maxLength": 50 },
        "feature3": { "field": "feature3", "type": "text", "minLength": 1, "maxLength": 50 },
        "feature4": { "field": "feature4", "type": "text", "minLength": 1, "maxLength": 50 },
        "feature_title": { "field": "feature_title", "type": "text", "minLength": 1, "maxLength": 10 },
        "product_name": { "field": "product_name", "type": "text", "minLength": 1, "maxLength": 10 },
        "samples": {
            "product_image": "https://example.com/nasal_drops.png",
            "feature1": "This nasal drop is good",
            "feature2": "Really great product",
            "feature3": "Clears nose with ease",
            "feature4": "Long lasting effect",
            "feature_title": "Features",
            "product_name": "Nasal Drops"
        },
        "fieldPrompt": {
            "product_image": "generate a prompt for a product image for the above idea. it should be a portrait image with aspect ratio of 1920 by 1080",
            "feature1": "Main feature 1 (e.g., 'This nasal drop is good') in under 50 chars",
            "feature2": "Main feature 2 (e.g., 'This nasal drop is really great product') in under 50 chars",
            "feature3": "Main feature 3 (e.g., 'Clears nose with ease') in under 50 chars",
            "feature4": "Additional feature (e.g., 'Long lasting effect') in under 50 chars",
            "feature_title": "Section title (e.g., 'Features') in under 10 chars",
            "product_name": "Name of the product (e.g., 'Nasal Drops') in under 10 chars"
        }
    },
    "event_alert": {
        "company_name": { "field": "company_name", "type": "text", "minLength": 1, "maxLength": 50 },
        "event_type": { "field": "event_type", "type": "text", "minLength": 1, "maxLength": 20 },
        "event_date": { "field": "event_date", "type": "text", "minLength": 1, "maxLength": 20 },
        "event_time": { "field": "event_time", "type": "text", "minLength": 1, "maxLength": 22 },
        "event_highlight": { "field": "event_highlight", "type": "text", "minLength": 1, "maxLength": 200 },
        "register_details": { "field": "register_details", "type": "text", "minLength": 1, "maxLength": 100 },
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000, "isTransparentImage": True },
        "samples": {
            "company_name": "Dolze AI",
            "event_type": "FREE WEBINAR",
            "event_date": "July 16",
            "event_time": "10:00 AM - 12:00 PM",
            "event_highlight": "Learn AI innovations from industry experts",
            "register_details": "Registration Link in bio",
            "product_image": "https://example.com/webinar_image.png"
        },
        "fieldPrompt": {
            "company_name": "Name of the company (e.g., 'Dolze AI')",
            "event_type": "Type of event (e.g., 'FREE WEBINAR') in under 20 chars",
            "event_date": "Date of the event (e.g., 'July 16') in under 20 chars",
            "event_time": "Time of the event (e.g., '10:00 AM - 12:00 PM') in under 20 chars",
            "event_highlight": "Main highlight of the event in under 200 chars",
            "register_details": "Registration information (e.g., 'Registration Link in bio') in under 100 chars",
            "product_image": "generate a prompt for a product image for the above idea. it should be a portrait image with aspect ratio of 1920 by 1080"
        }
    },
    "sale_alert": {
        "sale_heading": { "field": "sale_heading", "type": "text", "minLength": 1, "maxLength": 16 },
        "sale_description": { "field": "sale_description", "type": "text", "minLength": 1, "maxLength": 35 },
        "cta_text": { "field": "cta_text", "type": "text", "minLength": 1, "maxLength": 20 },
        "website_url": { "field": "website_url", "type": "url", "minLength": 1, "maxLength": 100 },
        "sale_text": { "field": "sale_text", "type": "text", "minLength": 1, "maxLength": 14 },
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000, "isTransparentImage": True },
        "samples": {
            "sale_heading": "Technology Sale",
            "sale_description": "Special Sale Only in August",
            "cta_text": "Shop Now!",
            "website_url": "www.dolze.ai",
            "sale_text": "30% off",
            "product_image": "https://example.com/sale_product.png"
        },
        "fieldPrompt": {
            "sale_heading": "Sale title (e.g., 'Technology Sale') in 2 words",
            "sale_description": "Sale description (e.g., 'Special Sale Only in August') in under 35 chars",
            "cta_text": "Call to action text (e.g., 'Shop Now!') in under 20 chars",
            "website_url": "Website URL (e.g., 'www.dolze.ai')",
            "sale_text": "Sale details (e.g., '30% off') in under 14 chars",
            "product_image": "generate a prompt for a product image for the above idea. it should be a portrait image with aspect ratio of 1080 by 1920"
        }
    },
    "testimonials": {
        "product_image": { "field": "product_image", "type": "image", "minLength": 0, "maxLength": 1000 },
        "name": { "field": "name", "type": "text", "minLength": 1, "maxLength": 15 },
        "greeting": { "field": "greeting", "type": "text", "minLength": 1, "maxLength": 20 },
        "designation": { "field": "designation", "type": "text", "minLength": 1, "maxLength": 500 },
        "social_handle": { "field": "social_handle", "type": "text", "minLength": 1, "maxLength": 50 },
        "samples": {
            "product_image": "https://example.com/testimonial_image.jpg",
            "name": "Sagar Giri",
            "greeting": "Meet our developers",
            "designation": "I have had a passion for coding since childhood.",
            "social_handle": "@dolze_ai"
        },
        "fieldPrompt": {
            "product_image": "generate a prompt for a product image for the above idea. it should be a portrait image with aspect ratio of 1920 by 1080",
            "name": "Full name of the person (e.g., 'Sagar Giri') in under 15 chars",
            "greeting": "Introduction text (e.g., 'Meet our developers') in under 20 chars",
            "designation": "Testimonial quote in quotes (e.g., 'I have had a passion...') in under 500 chars",
            "social_handle": "Social media handle (e.g., '@dolze_ai') in under 50 chars"
        }
    },
    "event_announcement": {
        "event_image": { "field": "event_image", "type": "image", "minLength": 0, "maxLength": 1000 },
        "event_name": { "field": "event_name", "type": "text", "minLength": 1, "maxLength": 10 },
        "event_description": { "field": "event_description", "type": "text", "minLength": 1, "maxLength": 150 },
        "company_name": { "field": "company_name", "type": "text", "minLength": 1, "maxLength": 30 },
        "samples": {
            "event_image": "https://example.com/event_circle.jpg",
            "event_name": "Sale Alert",
            "event_description": "Join our exclusive sale event this weekend!",
            "company_name": "Dolze AI"
        },
        "fieldPrompt": {
            "event_image": "generate a prompt for an event-related image that will be displayed in a circular format",
            "event_name": "Name of the event (e.g., 'Sale alert') in under 10 chars",
            "event_description": "Brief description of the event in under 100 chars",
            "company_name": "Name of the company hosting the event in under 50 chars"
        }
    }
}

    def get_template_names(self) -> List[str]:
        """
        Get a list of all available template names.

        Returns:
            List of template names
        """
        return list(self.templates.keys())

    def create_template_instance(
        self, name: str, variables: Optional[Dict[str, Any]] = None
    ) -> Optional[Template]:
        """
        Create a template instance with the given variables.

        Args:
            name: Name of the template
            variables: Dictionary of variables to substitute in the template

        Returns:
            A Template instance or None if the template is not found
        """
        template_config = self.get_template(name)
        if not template_config:
            return None

        # Create a deep copy of the config to avoid modifying the original
        config = json.loads(json.dumps(template_config))

        # Apply variable substitution if variables are provided
        if variables:
            config = self._substitute_variables(config, variables)

        return Template.from_config(config)

    def _substitute_variables(self, config: Any, variables: Dict[str, Any]) -> Any:
        """
        Recursively substitute variables in the template configuration.

        Args:
            config: Template configuration or part of it
            variables: Dictionary of variables to substitute

        Returns:
            Configuration with variables substituted
        """
        if isinstance(config, dict):
            result = {}
            for key, value in config.items():
                result[key] = self._substitute_variables(value, variables)
            return result
        elif isinstance(config, list):
            return [self._substitute_variables(item, variables) for item in config]
        elif isinstance(config, str):
            # Replace ${variable} with the corresponding value
            def replace_match(match):
                var_name = match.group(1)
                return str(variables.get(var_name, match.group(0)))

            return re.sub(r"\${([^}]+)}", replace_match, config)
        else:
            return config

    def render_template(
        self,
        template_name: str,
        variables: Dict[str, Any],
        output_path: Optional[str] = None,
    ) -> Optional[Image.Image]:
        """
        Render a template with the given variables.

        Args:
            template_name: Name of the template to render
            variables: Dictionary of variables to substitute in the template
            output_path: Optional path to save the rendered image

        Returns:
            Rendered PIL Image or None if rendering fails
        """
        template = self.create_template_instance(template_name, variables)
        if not template:
            return None

        # Render the template
        rendered_image = template.render()

        # Save to file if output path is provided
        if output_path:
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
            rendered_image.save(output_path)

        return rendered_image


# Singleton instance for easy access
_instance = None


def get_template_registry(templates_dir: Optional[str] = None) -> TemplateRegistry:
    """
    Get the singleton instance of the template registry.

    Args:
        templates_dir: Optional directory containing template definitions

    Returns:
        TemplateRegistry instance
    """
    global _instance
    if _instance is None:
        _instance = TemplateRegistry(templates_dir)
    return _instance