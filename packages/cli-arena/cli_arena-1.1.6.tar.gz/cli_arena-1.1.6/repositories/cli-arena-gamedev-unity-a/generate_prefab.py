#!/usr/bin/env python3
import json
import sys
import os
import argparse
from pathlib import Path
def validate_image_file(image_path):
    """Validate that the image file exists and has a supported format"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    
    valid_extensions = ['.png', '.jpg', '.jpeg', '.tga', '.bmp']
    file_ext = Path(image_path).suffix.lower()
    if file_ext not in valid_extensions:
        raise ValueError(f"Unsupported image format: {file_ext}. Supported formats: {valid_extensions}")
    
    return True
def validate_config_file(config_path):
    """Validate and load the JSON configuration file"""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")
    
    # Validate required fields
    required_fields = ['prefabName', 'pixelsPerUnit']
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required field in config: {field}")
    
    return config
def generate_prefab_cs_code(image_path, config, output_dir):
    """Generate C# code for Unity Editor script to create the prefab"""
    
    image_name = Path(image_path).stem
    prefab_name = config['prefabName']
    pixels_per_unit = config['pixelsPerUnit']
    components = config.get('components', [])
    
    cs_code = f'''using UnityEngine;
using UnityEditor;
using System.IO;
public class PrefabGenerator : MonoBehaviour
{{
    [MenuItem("Tools/Generate Prefab from Config")]
    public static void GeneratePrefab()
    {{
        // Load the sprite from Resources folder
        string spritePath = "Assets/Resources/{image_name}";
        Texture2D texture = AssetDatabase.LoadAssetAtPath<Texture2D>(spritePath + ".png");
        
        if (texture == null)
        {{
            Debug.LogError($"Could not load texture at {{spritePath}}");
            return;
        }}
        // Create sprite from texture
        string spriteAssetPath = spritePath + "_sprite.asset";
        Sprite sprite = Sprite.Create(texture, new Rect(0, 0, texture.width, texture.height), new Vector2(0.5f, 0.5f), {pixels_per_unit});
        AssetDatabase.CreateAsset(sprite, spriteAssetPath);
        // Create GameObject for prefab
        GameObject prefabObject = new GameObject("{prefab_name}");
        
        // Add SpriteRenderer component
        SpriteRenderer spriteRenderer = prefabObject.AddComponent<SpriteRenderer>();
        spriteRenderer.sprite = sprite;
'''
    # Add components from config
    for component in components:
        comp_type = component['type']
        if comp_type == 'BoxCollider2D':
            size = component.get('size', {'x': 1.0, 'y': 1.0})
            cs_code += f'''
        // Add {comp_type}
        BoxCollider2D boxCollider = prefabObject.AddComponent<BoxCollider2D>();
        boxCollider.size = new Vector2({size['x']}f, {size['y']}f);'''
        
        elif comp_type == 'Rigidbody2D':
            gravity_scale = component.get('gravityScale', 1.0)
            cs_code += f'''
        // Add {comp_type}
        Rigidbody2D rigidBody = prefabObject.AddComponent<Rigidbody2D>();
        rigidBody.gravityScale = {gravity_scale}f;'''
        
        elif comp_type == 'CircleCollider2D':
            radius = component.get('radius', 0.5)
            cs_code += f'''
        // Add {comp_type}
        CircleCollider2D circleCollider = prefabObject.AddComponent<CircleCollider2D>();
        circleCollider.radius = {radius}f;'''
    cs_code += f'''
        // Create prefab directory if it doesn't exist
        string prefabDir = "Assets/Prefabs";
        if (!Directory.Exists(prefabDir))
        {{
            Directory.CreateDirectory(prefabDir);
            AssetDatabase.Refresh();
        }}
        // Save as prefab
        string prefabPath = $"{{prefabDir}}/{prefab_name}.prefab";
        PrefabUtility.SaveAsPrefabAsset(prefabObject, prefabPath);
        
        // Clean up the temporary GameObject
        DestroyImmediate(prefabObject);
        
        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        
        Debug.Log($"Prefab created at {{prefabPath}}");
    }}
}}
'''
    
    return cs_code
def main():
    parser = argparse.ArgumentParser(description='Generate Unity prefabs from image and config files')
    parser.add_argument('image', help='Path to the input image file')
    parser.add_argument('config', help='Path to the JSON configuration file')
    parser.add_argument('-o', '--output', default='src/Editor', help='Output directory for generated files')
    
    args = parser.parse_args()
    
    try:
        # Validate inputs
        validate_image_file(args.image)
        config = validate_config_file(args.config)
        
        # Create output directory
        os.makedirs(args.output, exist_ok=True)
        
        # Generate C# code
        cs_code = generate_prefab_cs_code(args.image, config, args.output)
        
        # Write the C# file
        output_file = os.path.join(args.output, 'PrefabGenerator.cs')
        with open(output_file, 'w') as f:
            f.write(cs_code)
        
        print(f"✓ Generated Unity Editor script: {output_file}")
        print(f"✓ Prefab will be named: {config['prefabName']}")
        print("✓ To generate the prefab in Unity:")
        print("  1. Copy your image to Assets/Resources/")
        print("  2. Open Unity Editor")
        print("  3. Go to Tools > Generate Prefab from Config")
        
        return 0
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
if __name__ == '__main__':
    sys.exit(main())
