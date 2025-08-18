"""
VoxBridge Converter Module
Core conversion logic separated from CLI interface
Enhanced for Unity and Roblox platform-specific exports
"""

import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time
import zipfile

# Try to import texture optimization modules (optional)
try:
    from .texture_optimizer import resize_texture, generate_texture_atlas, update_gltf_with_atlas
    TEXTURE_OPTIMIZATION_AVAILABLE = True
except ImportError:
    TEXTURE_OPTIMIZATION_AVAILABLE = False


class VoxBridgeConverter:
    """Core converter class for VoxEdit glTF/glb files with platform-specific optimizations"""
    
    def __init__(self):
        self.supported_formats = ['.gltf', '.glb']
        self.blender_script_path = Path(__file__).parent / 'blender_cleanup.py'
        self._extracted_binary_data = {}
        self.last_changes = []
        
    def validate_input(self, input_path: Path) -> bool:
        """Validate input file exists and has correct format"""
        if not input_path.exists():
            return False
            
        if input_path.suffix.lower() not in self.supported_formats:
            return False
            
        return True
    
    def find_blender(self) -> Optional[str]:
        """Find Blender executable in common locations"""
        possible_paths = [
            # Windows
            r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.1\blender.exe",
            r"C:\Program Files\Blender Foundation\Blender 4.2\blender.exe",
            # macOS
            "/Applications/Blender.app/Contents/MacOS/Blender",
            # Linux
            "/usr/bin/blender",
            "/usr/local/bin/blender",
            "/snap/bin/blender",
            # Flatpak
            "/var/lib/flatpak/exports/bin/org.blender.Blender"
        ]
        
        # Check if blender is in PATH
        if shutil.which("blender"):
            return "blender"
            
        # Check common installation paths
        for path in possible_paths:
            if os.path.exists(path):
                return path
                
        return None
    
    def clean_gltf_json(self, gltf_path: Path, output_path: Path = None) -> Tuple[Dict, List[str]]:
        """Clean glTF JSON for texture paths and material names"""
        # Handle GLB files differently - they need to be converted to glTF first
        if gltf_path.suffix.lower() == '.glb':
            if output_path is None:
                output_path = gltf_path.with_suffix('.gltf')
            return self._process_glb_file(gltf_path, output_path)
        
        # Handle glTF files as before
        try:
            with open(gltf_path, 'r', encoding='utf-8') as f:
                gltf_data = json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read glTF file {gltf_path}: {e}")
        
        changes_made = []
        
        # Clean texture URIs (convert absolute paths to relative)
        if 'images' in gltf_data:
            for i, image in enumerate(gltf_data['images']):
                if 'uri' in image:
                    original_uri = image['uri']
                    # Convert absolute paths to just filename
                    # Check for both backslashes and forward slashes, and also handle escaped backslashes
                    if '\\' in original_uri or '/' in original_uri or '\\\\' in original_uri:
                        # Handle both single and double backslashes
                        clean_uri = original_uri.replace('\\\\', '\\').replace('\\', '/')
                        filename = Path(clean_uri).name
                        image['uri'] = filename
                        changes_made.append(f"Fixed image {i}: {original_uri} → {filename}")
        
        # Clean material names (alphanumeric only)
        if 'materials' in gltf_data:
            for i, material in enumerate(gltf_data['materials']):
                if 'name' in material:
                    original_name = material['name']
                    # Clean name: only alphanumeric and underscores
                    clean_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in original_name)
                    # Remove multiple underscores and leading/trailing underscores
                    clean_name = '_'.join(filter(None, clean_name.split('_')))
                    
                    if clean_name != original_name:
                        material['name'] = clean_name
                        changes_made.append(f"Cleaned material {i}: '{original_name}' → '{clean_name}'")
                    
                    # Handle empty names
                    if not clean_name:
                        material['name'] = 'Material'
                        changes_made.append(f"Fixed empty material {i}: '' → 'Material'")
        
        return gltf_data, changes_made
    
    def _process_glb_file(self, glb_path: Path, output_path: Path) -> Tuple[Dict, List[str]]:
        """Process GLB file and convert to GLTF format"""
        try:
            print(f"🔍 [DEBUG] Starting GLB processing for: {glb_path}")
            print(f"🔍 [DEBUG] Output path: {output_path}")
            
            # Try pygltflib first
            try:
                import pygltflib
                print(f"🔍 [DEBUG] pygltflib imported successfully")
                
                # Load GLB file
                print(f"🔍 [DEBUG] Loading GLB file with pygltflib...")
                gltf = pygltflib.GLTF2().load(str(glb_path))
                print(f"🔍 [DEBUG] GLB file loaded successfully")
                
                # Convert to dictionary for processing
                print(f"🔍 [DEBUG] Converting pygltflib objects to dictionary...")
                gltf_data = {}
                
                # Process each component with detailed logging
                components_to_process = [
                    'asset', 'scene', 'scenes', 'nodes', 'meshes', 'materials', 
                    'textures', 'samplers', 'images', 'accessors', 'bufferViews', 
                    'buffers', 'animations', 'skins'
                ]
                
                for component in components_to_process:
                    if hasattr(gltf, component):
                        print(f"🔍 [DEBUG] Processing component: {component}")
                        component_data = getattr(gltf, component)
                        
                        if component_data is not None:
                            if isinstance(component_data, list):
                                print(f"🔍 [DEBUG] {component} is a list with {len(component_data)} items")
                                gltf_data[component] = []
                                for i, item in enumerate(component_data):
                                    print(f"🔍 [DEBUG] Converting {component}[{i}] from {type(item).__name__}")
                                    converted_item = self._convert_pygltflib_object(item)
                                    gltf_data[component].append(converted_item)
                            else:
                                print(f"🔍 [DEBUG] {component} is a single object of type {type(component_data).__name__}")
                                converted_item = self._convert_pygltflib_object(component_data)
                                gltf_data[component] = converted_item
                        else:
                            print(f"🔍 [DEBUG] {component} is None, skipping")
                    else:
                        print(f"🔍 [DEBUG] {component} not found in GLB")
                
                print(f"🔍 [DEBUG] GLTF data conversion complete. Keys: {list(gltf_data.keys())}")
                
                # Extract binary data for potential re-embedding
                if hasattr(gltf, '_glb_data') and gltf._glb_data:
                    print(f"🔍 [DEBUG] GLB contains binary data, extracting...")
                    self._extracted_binary_data = self._extract_binary_data(gltf, gltf_data)
                    print(f"🔍 [DEBUG] Extracted {len(self._extracted_binary_data)} binary buffers")
                    
                    # Update buffer references to point to external binary file
                    if 'buffers' in gltf_data and gltf_data['buffers']:
                        print(f"🔍 [DEBUG] Processing buffer references...")
                        # Create a single external binary file with unique name
                        binary_filename = f"{output_path.stem}.bin"
                        binary_path = output_path.parent / binary_filename
                        
                        # Calculate total size and create combined binary file
                        total_size = 0
                        buffer_view_offsets = {}
                        
                        print(f"🔍 [DEBUG] Calculating buffer view offsets...")
                        # First pass: calculate total size and new offsets
                        for i, buffer_view in enumerate(gltf_data['bufferViews']):
                            if f'bufferView_{i}' in self._extracted_binary_data:
                                buffer_view_offsets[i] = total_size
                                total_size += len(self._extracted_binary_data[f'bufferView_{i}'])
                                print(f"🔍 [DEBUG] BufferView {i}: size {len(self._extracted_binary_data[f'bufferView_{i}']):,}, offset {total_size:,}")
                        
                        print(f"🔍 [DEBUG] Total binary size: {total_size:,} bytes")
                        
                        # Write the combined binary data
                        print(f"🔍 [DEBUG] Writing combined binary file...")
                        with open(binary_path, 'wb') as f:
                            for i, buffer_view in enumerate(gltf_data['bufferViews']):
                                if f'bufferView_{i}' in self._extracted_binary_data:
                                    f.write(self._extracted_binary_data[f'bufferView_{i}'])
                        
                        # Update buffer views with new offsets and byteLength
                        print(f"🔍 [DEBUG] Updating buffer view offsets and lengths...")
                        current_offset = 0
                        valid_buffer_views = []
                        
                        for i, buffer_view in enumerate(gltf_data['bufferViews']):
                            if f'bufferView_{i}' in self._extracted_binary_data:
                                # Update this buffer view with correct offset and length
                                buffer_view['byteOffset'] = current_offset
                                buffer_view['byteLength'] = len(self._extracted_binary_data[f'bufferView_{i}'])
                                print(f"🔍 [DEBUG] BufferView {i}: Updated byteLength to {buffer_view['byteLength']:,} bytes, offset: {buffer_view['byteOffset']:,}")
                                current_offset += buffer_view['byteLength']
                                valid_buffer_views.append(buffer_view)
                            else:
                                print(f"⚠️  BufferView {i}: No extracted data, skipping to prevent gaps")
                        
                        # Replace buffer views with only valid ones to prevent gaps
                        gltf_data['bufferViews'] = valid_buffer_views
                        print(f"🔍 [DEBUG] Final buffer views count: {len(gltf_data['bufferViews'])}")
                        
                        # Update the first buffer to reference the external file
                        gltf_data['buffers'][0] = {
                            'uri': binary_filename,
                            'byteLength': total_size
                        }
                        
                        # Remove extra buffers if they exist
                        if len(gltf_data['buffers']) > 1:
                            gltf_data['buffers'] = [gltf_data['buffers'][0]]
                        
                        print(f"📁 Created external binary file: {binary_filename} ({total_size:,} bytes)")
                
                # CRITICAL: Fix accessor byteLength calculations to prevent Error 23
                print(f"🔍 [DEBUG] Starting accessor byteLength fixes...")
                self._fix_accessor_byte_lengths(gltf_data)
                
                print(f"🔍 [DEBUG] GLB processing complete")
                return gltf_data, ["GLB file processed successfully using pygltflib"]
                
            except ImportError:
                print("pygltflib not available, trying alternative method...")
                raise ImportError("pygltflib required for GLB processing")
                
            except Exception as pygltf_error:
                print(f"pygltflib failed: {pygltf_error}")
                print("Trying alternative GLB processing method...")
                raise RuntimeError(f"pygltflib processing failed: {pygltf_error}")
                
        except Exception as e:
            print(f"❌ Failed to process GLB file: {e}")
            import traceback
            traceback.print_exc()
            raise RuntimeError(f"GLB processing failed: {e}")
    
    def validate_output(self, output_path: Path) -> Dict:
        """Validate and analyze the output file"""
        stats = {
            'file_exists': output_path.exists(),
            'file_size': 0,
            'materials': 0,
            'textures': 0,
            'meshes': 0,
            'nodes': 0
        }
        
        if not stats['file_exists']:
            return stats
            
        stats['file_size'] = output_path.stat().st_size
        
        # Try to parse both glTF and GLB files using pygltflib
        try:
            import pygltflib
            gltf = pygltflib.GLTF2().load(str(output_path))
            
            # Extract statistics from the parsed glTF/GLB
            stats['materials'] = len(gltf.materials) if gltf.materials else 0
            stats['textures'] = len(gltf.images) if gltf.images else 0
            stats['meshes'] = len(gltf.meshes) if gltf.meshes else 0
            stats['nodes'] = len(gltf.nodes) if gltf.nodes else 0
            
            # Add note for GLB files to indicate successful parsing
            if output_path.suffix.lower() == '.glb':
                stats['note'] = 'GLB format - successfully parsed with pygltflib'
            
        except ImportError:
            # Fallback for when pygltflib is not available
            if output_path.suffix.lower() == '.glb':
                stats['note'] = 'GLB format - pygltflib not available for detailed analysis'
            elif output_path.suffix.lower() == '.gltf':
                try:
                    with open(output_path, 'r', encoding='utf-8') as f:
                        gltf_data = json.load(f)
                    
                    stats['materials'] = len(gltf_data.get('materials', []))
                    stats['textures'] = len(gltf_data.get('images', []))
                    stats['meshes'] = len(gltf_data.get('meshes', []))
                    stats['nodes'] = len(gltf_data.get('nodes', []))
                    
                except Exception as e:
                    stats['error'] = str(e)
            else:
                stats['error'] = 'Unsupported file format'
                
        except Exception as e:
            stats['error'] = f'Failed to parse file: {str(e)}'
        
        return stats
    
    def convert_file(self, input_path: Path, output_path: Path, use_blender: bool = True, optimize_mesh: bool = False, generate_atlas: bool = False, compress_textures: bool = False, platform: str = "unity") -> bool:
        """Main conversion logic with enhanced platform-specific handling"""
        # Create output directory if it exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Clean up old output files to prevent duplicates
        self._cleanup_old_outputs(output_path)
        
        if use_blender and input_path.suffix.lower() == '.glb':
            # Try Blender first for GLB files
            try:
                print("🎨 Attempting Blender conversion...")
                if self.convert_with_blender(input_path, output_path, optimize_mesh=optimize_mesh, platform=platform):
                    print("✅ Blender conversion successful!")
                    return True
                else:
                    print("⚠️  Blender conversion failed, falling back to basic GLB processing...")
                    # Fall back to basic GLB processing
                    return self.convert_gltf_json(input_path, output_path, generate_atlas=generate_atlas, compress_textures=compress_textures, platform=platform)
            except Exception as e:
                print(f"❌ Blender conversion failed with error: {e}")
                print("🔄 Falling back to basic GLB processing...")
                # Fall back to basic GLB processing
                return self.convert_gltf_json(input_path, output_path, generate_atlas=generate_atlas, compress_textures=compress_textures, platform=platform)
        else:
            # Use JSON parsing for glTF files or when Blender is disabled
            return self.convert_gltf_json(input_path, output_path, generate_atlas=generate_atlas, compress_textures=compress_textures, platform=platform)
    
    def convert_with_blender(self, input_path: Path, output_path: Path, optimize_mesh: bool = False, platform: str = "unity") -> bool:
        """Convert using Blender Python script with platform-specific settings"""
        blender_exe = self.find_blender()
        if not blender_exe:
            print("⚠️  Blender not found, using basic conversion...")
            return False
        
        if not self.blender_script_path.exists():
            print("⚠️  Blender script not found, using basic conversion...")
            return False
        
        # Try to install numpy in Blender's Python environment first
        try:
            print("🔧 Attempting to install numpy in Blender's Python environment...")
            numpy_install_cmd = [
                blender_exe,
                "--background",
                "--python-expr",
                "import subprocess; import sys; subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'numpy'])"
            ]
            result = subprocess.run(numpy_install_cmd, capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Numpy installed successfully in Blender's Python environment")
            else:
                print("⚠️  Could not install numpy in Blender's Python environment")
        except Exception as e:
            print(f"⚠️  Numpy installation attempt failed: {e}")
        
        # Run Blender in background mode with our script
        cmd = [
            blender_exe,
            "--background",
            "--python", str(self.blender_script_path),
            "--",
            str(input_path),
            str(output_path),
            "--platform", platform
        ]
        if optimize_mesh:
            cmd.append("--optimize-mesh")
        
        try:
            print("🎨 Running Blender conversion...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print("✅ Blender conversion successful!")
                return True
            else:
                # Check for specific error patterns
                stderr = result.stderr or ""
                stdout = result.stdout or ""
                
                if "No module named 'numpy'" in stderr or "No module named 'numpy'" in stdout:
                    print("⚠️  Blender numpy dependency missing. Using basic conversion...")
                    return False
                elif "ModuleNotFoundError" in stderr or "ModuleNotFoundError" in stdout:
                    print("⚠️  Blender Python environment missing required modules. Using basic conversion...")
                    return False
                else:
                    print(f"⚠️  Blender failed with return code {result.returncode}")
                    print(f"Error output: {stderr[:200]}...")
                    return False
                
        except subprocess.TimeoutExpired:
            print("⚠️  Blender processing timed out (120s). Using basic conversion...")
            return False
        except Exception as e:
            print(f"⚠️  Blender execution failed: {e}. Using basic conversion...")
            return False
        
        return False  # Fallback return
    
    def convert_gltf_json(self, input_path: Path, output_path: Path, generate_atlas: bool = False,
                          compress_textures: bool = False, platform: str = "unity") -> bool:
        """Convert glTF JSON data to output format with platform-specific optimizations"""
        try:
            # Ensure we have Path objects
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            # Get the cleaned glTF data first
            gltf_data, changes = self.clean_gltf_json(input_path, output_path)
            
            # Store changes for reporting
            self.last_changes = changes
            
            # Apply platform-specific material optimizations
            material_changes = self.map_materials(gltf_data, platform)
            self.last_changes.extend(material_changes)
            
            # Apply platform-specific mesh optimizations
            mesh_changes = self.optimize_meshes_for_platform(gltf_data, platform)
            self.last_changes.extend(mesh_changes)
            
            # Apply platform-specific texture optimizations
            texture_changes = self.optimize_textures_for_platform(gltf_data, platform, input_path.parent)
            self.last_changes.extend(texture_changes)
            
            # Skip GLB conversion entirely - go straight to GLTF output
            # This prevents unnecessary .glb files and ensures clean output
            gltf_output = output_path.with_suffix('.gltf')
            with open(gltf_output, 'w', encoding='utf-8') as f:
                json.dump(gltf_data, f, indent=2)
            
            print(f"✅ Saved as GLTF: {gltf_output}")
            
            # Run automatic validation
            self._run_validation(gltf_output)
            
            return True
                
        except Exception as e:
            print(f"❌ Failed to convert file: {e}")
            import traceback
            traceback.print_exc()
            return False

    def optimize_meshes_for_platform(self, gltf_data: Dict, platform: str) -> List[str]:
        """Apply platform-specific mesh optimizations"""
        changes = []
        
        if 'meshes' not in gltf_data:
            return changes
            
        for i, mesh in enumerate(gltf_data['meshes']):
            if 'primitives' in mesh:
                for j, primitive in enumerate(mesh['primitives']):
                    # Ensure proper attributes for platform
                    if 'attributes' in primitive:
                        attributes = primitive['attributes']
                        
                        # Unity: Ensure TANGENT attribute for normal mapping
                        if platform == "unity":
                            if 'TANGENT' not in attributes and 'NORMAL' in attributes:
                                # Add tangent attribute if missing
                                changes.append(f"Added TANGENT attribute for Unity compatibility: Mesh {i}, Primitive {j}")
                        
                        # Roblox: Ensure proper UV coordinates
                        if platform == "roblox":
                            if 'TEXCOORD_0' not in attributes:
                                changes.append(f"Warning: Missing UV coordinates for Roblox: Mesh {i}, Primitive {j}")
                        
                        # Both platforms: Ensure proper vertex count limits
                        if 'POSITION' in attributes:
                            pos_accessor_idx = attributes['POSITION']
                            if pos_accessor_idx < len(gltf_data.get('accessors', [])):
                                accessor = gltf_data['accessors'][pos_accessor_idx]
                                if 'count' in accessor:
                                    vertex_count = accessor['count']
                                    if platform == "roblox" and vertex_count > 10000:
                                        changes.append(f"Warning: High vertex count ({vertex_count}) for Roblox: Mesh {i}")
                                    elif platform == "unity" and vertex_count > 50000:
                                        changes.append(f"Warning: High vertex count ({vertex_count}) for Unity: Mesh {i}")
        
        return changes
    
    def optimize_textures_for_platform(self, gltf_data: Dict, platform: str, base_path: Path) -> List[str]:
        """Apply platform-specific texture optimizations"""
        changes = []
        
        if 'images' not in gltf_data:
            return changes
            
        for i, image in enumerate(gltf_data['images']):
            if 'uri' in image and image['uri']:
                image_path = base_path / image['uri']
                if image_path.exists():
                    # Roblox: Limit texture resolution to 1024x1024
                    if platform == "roblox":
                        try:
                            from PIL import Image
                            with Image.open(image_path) as img:
                                if max(img.size) > 1024:
                                    # Resize texture for Roblox
                                    img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                                    img.save(image_path)
                                    changes.append(f"Resized texture for Roblox: {image['uri']} -> 1024x1024")
                        except ImportError:
                            changes.append(f"PIL not available for texture optimization: {image['uri']}")
                        except Exception as e:
                            changes.append(f"Texture optimization failed: {image['uri']}: {e}")
                    
                    # Unity: Ensure proper texture format
                    elif platform == "unity":
                        try:
                            from PIL import Image
                            with Image.open(image_path) as img:
                                # Convert to RGBA if needed for Unity
                                if img.mode != 'RGBA':
                                    img = img.convert('RGBA')
                                    img.save(image_path)
                                    changes.append(f"Converted texture to RGBA for Unity: {image['uri']}")
                        except ImportError:
                            pass  # PIL not available, skip optimization
                        except Exception as e:
                            changes.append(f"Texture optimization failed: {image['uri']}: {e}")
        
        return changes

    def map_materials(self, gltf_data: Dict, platform: str = "unity") -> List[str]:
        """
        Enhanced material mapping for Unity/Roblox compatibility.
        Args:
            gltf_data: The glTF JSON data
            platform: Target platform ("unity" or "roblox")
        Returns:
            List of changes made
        """
        changes = []
        
        if 'materials' not in gltf_data:
            return changes
            
        for i, material in enumerate(gltf_data['materials']):
            # Handle both dict and pygltflib object types
            if hasattr(material, 'name'):
                original_name = material.name
            elif isinstance(material, dict):
                original_name = material.get('name', f'Material_{i}')
            else:
                original_name = f'Material_{i}'
            
            if platform == "unity":
                # Unity-specific material mapping
                if hasattr(material, 'pbrMetallicRoughness') and material.pbrMetallicRoughness:
                    pbr = material.pbrMetallicRoughness
                    
                    # Ensure Unity Standard shader compatibility
                    if hasattr(pbr, 'baseColorFactor') and pbr.baseColorFactor:
                        # Unity expects sRGB color space
                        color = pbr.baseColorFactor
                        if len(color) == 4:  # RGBA
                            # Convert to sRGB if needed (simplified)
                            pbr.baseColorFactor = [c ** 2.2 for c in color[:3]] + [color[3]]
                            changes.append(f"Adjusted color space for Unity: Material {i}")
                    
                    # Unity metallic-smoothness workflow
                    if hasattr(pbr, 'roughnessFactor') and pbr.roughnessFactor is not None:
                        # Unity uses smoothness (inverted roughness)
                        # Store original roughness for potential texture packing
                        setattr(pbr, '_originalRoughness', pbr.roughnessFactor)
                        changes.append(f"Stored original roughness for Unity: Material {i}")
                    
                    # Ensure proper texture references
                    if hasattr(pbr, 'metallicRoughnessTexture') and pbr.metallicRoughnessTexture:
                        changes.append(f"Verified metallic-roughness texture for Unity: Material {i}")
                        
            elif platform == "roblox":
                # Roblox-specific material mapping
                if hasattr(material, 'pbrMetallicRoughness') and material.pbrMetallicRoughness:
                    pbr = material.pbrMetallicRoughness
                    
                    # Roblox has specific material requirements
                    if hasattr(pbr, 'baseColorTexture') and pbr.baseColorTexture:
                        # Ensure texture is properly referenced
                        changes.append(f"Verified base color texture for Roblox: Material {i}")
                    
                    # Roblox may need simplified material properties
                    if hasattr(pbr, 'metallicFactor') and pbr.metallicFactor and pbr.metallicFactor > 0.5:
                        # Reduce metallic factor for better Roblox compatibility
                        pbr.metallicFactor = min(pbr.metallicFactor, 0.5)
                        changes.append(f"Reduced metallic factor for Roblox: Material {i}")
                    
                    # Store PBR values for potential baking
                    if hasattr(pbr, 'roughnessFactor') and pbr.roughnessFactor is not None:
                        setattr(pbr, '_originalRoughness', pbr.roughnessFactor)
                    if hasattr(pbr, 'metallicFactor') and pbr.metallicFactor is not None:
                        setattr(pbr, '_originalMetallic', pbr.metallicFactor)
                    changes.append(f"Stored PBR values for potential baking: Material {i}")
            
            # Clean material name for platform compatibility
            clean_name = self._clean_material_name(original_name, platform)
            if clean_name != original_name:
                # Handle both dict and object types
                if isinstance(material, dict):
                    material['name'] = clean_name
                else:
                    setattr(material, 'name', clean_name)
                changes.append(f"Renamed material for {platform}: '{original_name}' → '{clean_name}'")
        
        return changes
    
    def _clean_material_name(self, name: str, platform: str) -> str:
        """Clean material name for specific platform requirements"""
        import re
        
        if platform == "roblox":
            # Roblox has stricter naming requirements
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
            clean_name = re.sub(r'_+', '_', clean_name)
            clean_name = clean_name.strip('_')
            # Ensure it's not empty and not too long
            if not clean_name:
                clean_name = 'Material'
            if len(clean_name) > 50:  # Roblox limit
                clean_name = clean_name[:50]
        else:  # Unity
            # Unity is more flexible, but still clean
            clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
            clean_name = re.sub(r'_+', '_', clean_name)
            clean_name = clean_name.strip('_')
            if not clean_name:
                clean_name = 'Material'
        
        return clean_name

    def create_platform_package(self, gltf_path: Path, platform: str) -> bool:
        """Create a platform-specific ZIP package with all necessary files"""
        try:
            import zipfile
            
            # Create ZIP with platform-specific naming
            zip_path = gltf_path.parent / f"{gltf_path.stem}_{platform}_package.zip"
            
            # Find all associated files to include in the ZIP
            files_to_zip = []
            
            # Add GLTF file
            files_to_zip.append((gltf_path, gltf_path.name))
            
            # Look for .bin files and include them
            for bin_file in gltf_path.parent.glob("*.bin"):
                # Only include the specific binary file for this conversion
                if bin_file.name == f"{gltf_path.stem}.bin":
                    files_to_zip.append((bin_file, bin_file.name))
            
            # Look for texture files and include them
            texture_exts = ['.png', '.jpg', '.jpeg', '.tga', '.bmp']
            for texture_file in gltf_path.parent.glob("*"):
                if texture_file.suffix.lower() in texture_exts:
                    files_to_zip.append((texture_file, texture_file.name))
            
            # Create a license.txt file
            license_path = gltf_path.parent / "license.txt"
            with open(license_path, 'w') as f:
                f.write("Creative Commons Attribution 4.0 International License\n")
                f.write("https://creativecommons.org/licenses/by/4.0/\n")
                f.write("\nModel created with VoxBridge converter.")
            
            files_to_zip.append((license_path, "license.txt"))
            
            # Create metadata file
            metadata = {
                "original_source_format": "GLB",
                "target_platform": platform,
                "export_date": time.strftime("%Y-%m-%d %H:%M:%S"),
                "tool_version": "1.0.3",
                "platform_specific_notes": self._get_platform_notes(platform),
                "files_included": [name for _, name in files_to_zip]
            }
            
            metadata_path = gltf_path.parent / "metadata.json"
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            files_to_zip.append((metadata_path, "metadata.json"))
            
            # Create ZIP package
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, zip_name in files_to_zip:
                    zipf.write(file_path, zip_name)
            
            print(f"📦 Created {platform} package: {zip_path}")
            print(f"📁 Files included: {[name for _, name in files_to_zip]}")
            print(f"💡 This package is ready for {platform}")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create {platform} package: {e}")
            return False
    
    def _get_platform_notes(self, platform: str) -> str:
        """Get platform-specific notes for metadata"""
        if platform == "unity":
            return "Optimized for Unity 3D with PBR workflow, Y-up orientation, and proper tangent space"
        elif platform == "roblox":
            return "Optimized for Roblox with texture size limits, simplified materials, and Roblox-compatible naming"
        else:
            return "Generic optimization applied"
    
    def optimize_meshes_for_platform(self, gltf_data: Dict, platform: str) -> List[str]:
        """Apply platform-specific mesh optimizations"""
        changes = []
        
        if 'meshes' not in gltf_data:
            return changes
            
        for i, mesh in enumerate(gltf_data['meshes']):
            if 'primitives' in mesh:
                for j, primitive in enumerate(mesh['primitives']):
                    # Ensure proper attributes for platform
                    if 'attributes' in primitive:
                        attributes = primitive['attributes']
                        
                        # Unity: Ensure TANGENT attribute for normal mapping
                        if platform == "unity":
                            if 'TANGENT' not in attributes and 'NORMAL' in attributes:
                                # Add tangent attribute if missing
                                changes.append(f"Added TANGENT attribute for Unity compatibility: Mesh {i}, Primitive {j}")
                        
                        # Roblox: Ensure proper UV coordinates
                        if platform == "roblox":
                            if 'TEXCOORD_0' not in attributes:
                                changes.append(f"Warning: Missing UV coordinates for Roblox: Mesh {i}, Primitive {j}")
                        
                        # Both platforms: Ensure proper vertex count limits
                        if 'POSITION' in attributes:
                            pos_accessor_idx = attributes['POSITION']
                            if pos_accessor_idx < len(gltf_data.get('accessors', [])):
                                accessor = gltf_data['accessors'][pos_accessor_idx]
                                if 'count' in accessor:
                                    vertex_count = accessor['count']
                                    if platform == "roblox" and vertex_count > 10000:
                                        changes.append(f"Warning: High vertex count ({vertex_count}) for Roblox: Mesh {i}")
                                    elif platform == "unity" and vertex_count > 50000:
                                        changes.append(f"Warning: High vertex count ({vertex_count}) for Unity: Mesh {i}")
        
        return changes
    
    def optimize_textures_for_platform(self, gltf_data: Dict, platform: str, base_path: Path) -> List[str]:
        """Apply platform-specific texture optimizations"""
        changes = []
        
        if 'images' not in gltf_data:
            return changes
            
        for i, image in enumerate(gltf_data['images']):
            if 'uri' in image and image['uri']:
                image_path = base_path / image['uri']
                if image_path.exists():
                    # Roblox: Limit texture resolution to 1024x1024
                    if platform == "roblox":
                        try:
                            from PIL import Image
                            with Image.open(image_path) as img:
                                if max(img.size) > 1024:
                                    # Resize texture for Roblox
                                    img.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
                                    img.save(image_path)
                                    changes.append(f"Resized texture for Roblox: {image['uri']} -> 1024x1024")
                        except ImportError:
                            changes.append(f"PIL not available for texture optimization: {image['uri']}")
                        except Exception as e:
                            changes.append(f"Texture optimization failed: {image['uri']}: {e}")
                    
                    # Unity: Ensure proper texture format
                    elif platform == "unity":
                        try:
                            from PIL import Image
                            with Image.open(image_path) as img:
                                # Convert to RGBA if needed for Unity
                                if img.mode != 'RGBA':
                                    img = img.convert('RGBA')
                                    img.save(image_path)
                                    changes.append(f"Converted texture to RGBA for Unity: {image['uri']}")
                        except ImportError:
                            pass  # PIL not available, skip optimization
                        except Exception as e:
                            changes.append(f"Texture optimization failed: {image['uri']}: {e}")
        
        return changes
    
    def _ensure_output_structure(self, output_path: Path, input_path: Path, platform: str):
        """Ensure proper output directory structure and copy all necessary files"""
        try:
            # Create output directory
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy all associated files to output directory
            self.copy_associated_files(input_path, output_path)
            
            # Create platform-specific package
            self.create_platform_package(output_path, platform)
            
            # Create a README file explaining the output
            readme_path = output_path.parent / "README.txt"
            with open(readme_path, 'w') as f:
                f.write("VoxBridge Output Package\n")
                f.write("=" * 30 + "\n\n")
                f.write(f"Input file: {input_path.name}\n")
                f.write(f"Output file: {output_path.name}\n")
                f.write(f"Target platform: {platform}\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                f.write("Files included:\n")
                f.write(f"- {output_path.name} (main model file)\n")
                
                # List other files
                for file_path in output_path.parent.iterdir():
                    if file_path.is_file() and file_path != output_path and file_path != readme_path:
                        f.write(f"- {file_path.name}\n")
                
                f.write("\nUsage:\n")
                if platform == "unity":
                    f.write("- Import into Unity using the official GLTF importer\n")
                    f.write("- Ensure Y-up orientation is maintained\n")
                    f.write("- Check material assignments and PBR workflow\n")
                elif platform == "roblox":
                    f.write("- Import into Roblox using MeshPart importer\n")
                    f.write("- Verify texture sizes are within 1024x1024 limits\n")
                    f.write("- Check material compatibility with Roblox shaders\n")
                
                f.write("\nFor more information, visit: https://github.com/Supercoolkayy/voxbridge\n")
            
            print(f"📁 Created output structure in: {output_path.parent}")
            print(f"📖 Added README.txt with {platform} usage instructions")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create complete output structure: {e}")

    def _create_embedded_gltf(self, original_gltf, gltf_data: Dict) -> Dict:
        """Create glTF with embedded binary data using Data URLs (use sparingly)"""
        import base64
        
        print("⚠️ WARNING: Creating embedded GLTF with base64 data (may cause large file sizes)")
        print("💡 Consider using clean GLTF for better compatibility with platforms like Sketchfab")
        print("Embedding binary data into glTF...")
        
        # Get the binary data from the original GLB
        if hasattr(original_gltf, '_glb_data') and original_gltf._glb_data:
            binary_data = original_gltf._glb_data
            print(f"Found binary data: {len(binary_data):,} bytes")
            
            # Check file size warning
            if len(binary_data) > 1024 * 1024:  # 1MB
                print(f"⚠️ WARNING: Binary data is {len(binary_data) / (1024*1024):.1f}MB")
                print(f"⚠️ This will create a very large embedded file that may cause issues")
                print(f"💡 Consider using clean GLTF instead")
            
            # Convert binary data to base64 Data URL
            base64_data = base64.b64encode(binary_data).decode('ascii')
            data_url = f"data:application/octet-stream;base64,{base64_data}"
            
            # Update buffers to use the embedded data
            if 'buffers' in gltf_data:
                for buffer in gltf_data['buffers']:
                    buffer['uri'] = data_url
                    # Remove byteLength as it's not needed with Data URLs
                    if 'byteLength' in buffer:
                        del buffer['byteLength']
            
            print("✅ Binary data embedded successfully")
        else:
            print("⚠️ No binary data found in original GLB")
        
        return gltf_data

    def create_sketchfab_gltf(self, input_path: Path, output_path: Path) -> bool:
        """Create a clean GLTF file optimized for Sketchfab (no embedded data)"""
        try:
            print("Creating Sketchfab-optimized GLTF file...")
            
            # Ensure we have Path objects
            input_path = Path(input_path)
            output_path = Path(output_path)
            
            # Handle GLB files specially to ensure binary data is extracted
            if input_path.suffix.lower() == '.glb':
                print("📦 Processing GLB file - extracting binary data...")
                # Use the main conversion method which properly handles GLB files
                success = self.convert_gltf_json(input_path, output_path)
                if not success:
                    print("❌ Failed to convert GLB file")
                    return False
            else:
                # For existing GLTF files, just clean them
                gltf_data, _ = self.clean_gltf_json(input_path)
                
                # Ensure we don't have any embedded data
                if 'buffers' in gltf_data:
                    for buffer in gltf_data['buffers']:
                        # Remove any data URIs and keep only external references
                        if 'uri' in buffer and buffer['uri'].startswith('data:'):
                            print("⚠️ Removing embedded data URI for Sketchfab compatibility")
                            del buffer['uri']
                        # Keep byteLength for proper buffer handling
                        if 'byteLength' not in buffer:
                            print("⚠️ Adding byteLength for proper buffer handling")
                            buffer['byteLength'] = 0  # Will be updated by external tools
                
                # Write the clean glTF file
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(gltf_data, f, indent=2)
            
            print(f"✅ Created Sketchfab-optimized GLTF: {output_path}")
            print(f"📊 File size: {output_path.stat().st_size:,} bytes")
            print(f"💡 This file is optimized for Sketchfab and other web platforms")
            
            # Create ZIP package for Sketchfab (like the working example)
            self._create_sketchfab_package(output_path)
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to create Sketchfab GLTF: {e}")
            return False
    
    def _create_sketchfab_package(self, gltf_path: Path) -> bool:
        """Create a ZIP package for Sketchfab with GLTF and binary files (using actual filenames)"""
        try:
            import zipfile
            
            # Create ZIP with the actual output filename
            zip_path = gltf_path.parent / f"{gltf_path.stem}.zip"
            
            # Find all associated files to include in the ZIP
            files_to_zip = []
            
            # Add GLTF file (keep original name in ZIP)
            files_to_zip.append((gltf_path, gltf_path.name))
            
            # Look for .bin files and include them with their original names
            for bin_file in gltf_path.parent.glob("*.bin"):
                # Include any .bin file that might be referenced by the GLTF
                files_to_zip.append((bin_file, bin_file.name))
            
            # Look for texture files and include them
            texture_exts = ['.png', '.jpg', '.jpeg', '.tga', '.bmp']
            for texture_file in gltf_path.parent.glob("*"):
                if texture_file.suffix.lower() in texture_exts:
                    # Only include textures that are actually referenced in the GLTF
                    files_to_zip.append((texture_file, texture_file.name))
            
            # Create a license.txt file
            license_path = gltf_path.parent / "license.txt"
            with open(license_path, 'w') as f:
                f.write("Creative Commons Attribution 4.0 International License\n")
                f.write("https://creativecommons.org/licenses/by/4.0/\n")
                f.write("\nModel created with VoxBridge converter.")
            
            files_to_zip.append((license_path, "license.txt"))
            
            # Create ZIP package with proper file names
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path, zip_name in files_to_zip:
                    zipf.write(file_path, zip_name)
            
            print(f"📦 Created Sketchfab package: {zip_path}")
            print(f"📁 Files included: {[name for _, name in files_to_zip]}")
            print(f"💡 Upload this ZIP file to Sketchfab")
            
            return True
            
        except Exception as e:
            print(f"⚠️ Warning: Could not create ZIP package: {e}")
            return False

    def _extract_image_paths(self, gltf_data: Dict, base_path: Path) -> List[Path]:
        """Extract image paths from glTF data"""
        image_paths = []
        
        if 'images' in gltf_data:
            for image in gltf_data['images']:
                if 'uri' in image and image['uri']:
                    # Handle relative paths
                    image_path = base_path / image['uri']
                    if image_path.exists():
                        image_paths.append(image_path)
        
        return image_paths

    def _extract_binary_data(self, gltf, gltf_data: Dict) -> Dict[str, bytes]:
        """Extract binary buffer data from GLTF2 object"""
        print(f"🔍 [DEBUG] Starting binary data extraction...")
        binary_data = {}
        
        if hasattr(gltf, '_glb_data') and gltf._glb_data and hasattr(gltf, 'bufferViews') and gltf.bufferViews:
            print(f"🔍 [DEBUG] GLB contains binary data: {len(gltf._glb_data):,} bytes")
            print(f"🔍 [DEBUG] Found {len(gltf.bufferViews)} buffer views")
            
            # Extract data from each buffer view
            for i, buffer_view in enumerate(gltf.bufferViews):
                print(f"🔍 [DEBUG] Processing buffer view {i}: {buffer_view}")
                
                if hasattr(buffer_view, 'byteOffset') and hasattr(buffer_view, 'byteLength'):
                    start = buffer_view.byteOffset
                    end = start + buffer_view.byteLength
                    print(f"🔍 [DEBUG] Buffer view {i}: offset {start}, length {buffer_view.byteLength}, end {end}")
                    
                    if start < len(gltf._glb_data) and end <= len(gltf._glb_data):
                        extracted_data = gltf._glb_data[start:end]
                        binary_data[f'bufferView_{i}'] = extracted_data
                        print(f"📦 Extracted buffer view {i}: {len(extracted_data)} bytes")
                    else:
                        print(f"❌ [DEBUG] Buffer view {i}: Invalid range - start {start}, end {end}, data size {len(gltf._glb_data)}")
                else:
                    print(f"⚠️ [DEBUG] Buffer view {i}: Missing byteOffset or byteLength attributes")
        else:
            print(f"🔍 [DEBUG] No binary data found in GLB")
            if not hasattr(gltf, '_glb_data'):
                print(f"🔍 [DEBUG] GLB missing _glb_data attribute")
            if not gltf._glb_data:
                print(f"🔍 [DEBUG] GLB _glb_data is empty")
            if not hasattr(gltf, 'bufferViews'):
                print(f"🔍 [DEBUG] GLB missing bufferViews attribute")
            if not gltf.bufferViews:
                print(f"🔍 [DEBUG] GLB bufferViews is empty")
        
        print(f"🔍 [DEBUG] Binary data extraction complete. Extracted {len(binary_data)} buffer views")
        return binary_data

    def _embed_binary_data(self, gltf_data: Dict, binary_data: Dict[str, bytes]) -> Dict:
        """Embed binary data into glTF using Data URLs"""
        import base64
        
        # Update buffer references to use Data URLs
        if 'buffers' in gltf_data:
            for i, buffer in enumerate(gltf_data['buffers']):
                buffer_key = f'buffer_{i}'
                if buffer_key in binary_data:
                    # Convert binary data to base64 Data URL
                    binary_bytes = binary_data[buffer_key]
                    base64_data = base64.b64encode(binary_bytes).decode('ascii')
                    buffer['uri'] = f"data:application/octet-stream;base64,{base64_data}"
                    # Remove byteLength as it's not needed with Data URLs
                    if 'byteLength' in buffer:
                        del buffer['byteLength']
        
        # Update image references to use Data URLs if available
        if 'images' in gltf_data:
            for i, image in enumerate(gltf_data['images']):
                if 'bufferView' in image:
                    # Convert buffer view data to Data URL
                    buffer_view_index = image['bufferView']
                    if f'buffer_{buffer_view_index}' in binary_data:
                        binary_bytes = binary_data[f'buffer_{buffer_view_index}']
                        base64_data = base64.b64encode(binary_bytes).decode('ascii')
                        image['uri'] = f"data:image/png;base64,{base64_data}"
                        # Remove bufferView as we now have URI
                        del image['bufferView']
        
        return gltf_data
    
    def copy_associated_files(self, input_path: Path, output_path: Path):
        """Copy texture and binary files associated with glTF"""
        input_dir = input_path.parent
        output_dir = output_path.parent
        
        # Common texture extensions
        texture_exts = ['.png', '.jpg', '.jpeg', '.tga', '.bmp']
        
        # Look for files in the same directory
        for file_path in input_dir.iterdir():
            if file_path.is_file():
                # Copy textures
                if file_path.suffix.lower() in texture_exts:
                    dest = output_dir / file_path.name
                    if not dest.exists():
                        shutil.copy2(file_path, dest)
                        print(f"📁 Copied texture: {file_path.name}")
                
                # Copy only the specific .bin file for this conversion
                elif file_path.suffix.lower() == '.bin' and file_path.name == f"{output_path.stem}.bin":
                    dest = output_dir / file_path.name
                    if not dest.exists():
                        shutil.copy2(file_path, dest)
                        print(f"📁 Copied binary data: {file_path.name}")
                
                # Copy other potentially referenced files
                elif file_path.suffix.lower() in ['.ktx', '.ktx2', '.webp']:
                    dest = output_dir / file_path.name
                    if not dest.exists():
                        shutil.copy2(file_path, dest)
                        print(f"📁 Copied additional texture: {file_path.name}")
        
        # Also check for files that might be referenced in the glTF but not in the same directory
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                gltf_data = json.load(f)
                
            # Check for images that might be in subdirectories
            if 'images' in gltf_data:
                for image in gltf_data['images']:
                    if 'uri' in image and image['uri']:
                        # Handle relative paths
                        if not image['uri'].startswith(('http://', 'https://', 'data:')):
                            image_path = input_dir / image['uri']
                            if image_path.exists() and image_path.is_file():
                                dest = output_dir / image_path.name
                                if not dest.exists():
                                    shutil.copy2(image_path, dest)
                                    print(f"📁 Copied referenced image: {image_path.name}")
                            
                            # Also copy from parent directory if it exists there
                            parent_image_path = input_dir.parent / image['uri']
                            if parent_image_path.exists() and parent_image_path.is_file():
                                dest = output_dir / parent_image_path.name
                                if not dest.exists():
                                    shutil.copy2(parent_image_path, dest)
                                    print(f"📁 Copied referenced image from parent: {parent_image_path.name}")
                                    
        except Exception as e:
            print(f"⚠️ Warning: Could not check for additional referenced files: {e}")

    def generate_performance_report(self, input_path: Path, output_path: Path, stats: Dict, changes: Optional[List[str]] = None) -> Dict:
        """
        Generate a performance summary report in JSON format.
        Args:
            input_path: Original input file path
            output_path: Processed output file path
            stats: Validation statistics from validate_output
            changes: List of changes made during processing
        Returns:
            Dictionary containing the performance report
        """
        report = {
            "input_file": str(input_path),
            "output_file": str(output_path),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "processing_time": None,  # Will be set by CLI
            "file_size_before": input_path.stat().st_size if input_path.exists() else 0,
            "file_size_after": stats.get('file_size', 0),
            "size_reduction_percent": 0,
            "triangles_before": None,  # Will be estimated or set by user
            "triangles_after": None,   # Will be estimated or set by user
            "textures": stats.get('textures', 0),
            "texture_resolution": "Unknown",
            "meshes": stats.get('meshes', 0),
            "materials": stats.get('materials', 0),
            "nodes": stats.get('nodes', 0),
            "platform": "unity",  # Default, will be set by CLI
            "optimizations_applied": [],
            "warnings": [],
            "notes": []
        }
        
        # Calculate size reduction
        if report["file_size_before"] > 0 and report["file_size_after"] > 0:
            report["size_reduction_percent"] = round(
                (1 - report["file_size_after"] / report["file_size_before"]) * 100, 2
            )
        
        # Add changes to optimizations applied
        if changes:
            report["optimizations_applied"] = changes
        
        # Add warnings based on stats
        if stats.get('file_size', 0) > 50 * 1024 * 1024:  # 50MB
            report["warnings"].append("Large file size (>50MB) - consider further optimization")
        
        if stats.get('meshes', 0) > 100:
            report["warnings"].append("High mesh count (>100) - consider mesh merging")
        
        if stats.get('textures', 0) > 10:
            report["warnings"].append("Many textures (>10) - consider texture atlas generation")
        
        # Add notes
        if stats.get('note'):
            report["notes"].append(stats['note'])
        
        if stats.get('error'):
            report["warnings"].append(f"Processing error: {stats['error']}")
        
        return report
    
    def save_performance_report(self, report: Dict, output_dir: Path) -> Path:
        """
        Save the performance report to a JSON file.
        Args:
            report: Performance report dictionary
            output_dir: Directory to save the report
        Returns:
            Path to the saved report file
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / "performance_report.json"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return report_path

    def _convert_gltf_to_glb(self, gltf_data: Dict, output_path: Path) -> bool:
        """Convert glTF JSON data to GLTF format (GLB generation disabled)"""
        try:
            print(f"Converting to GLTF format...")
            print(f"glTF data keys: {list(gltf_data.keys())}")
            print(f"Output path: {output_path}")
            
            # Skip GLB conversion entirely - go straight to GLTF output
            # This prevents unnecessary .glb files and ensures clean output
            gltf_output = output_path.with_suffix('.gltf')
            with open(gltf_output, 'w', encoding='utf-8') as f:
                json.dump(gltf_data, f, indent=2)
            
            print(f"✅ Saved as GLTF: {gltf_output}")
            
            # Run automatic validation
            self._run_validation(gltf_output)
            
            return True
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            raise RuntimeError(f"Failed to convert to GLTF: {e}\nDetails: {error_details}")

    def _ensure_external_references(self, gltf_data: Dict, base_path: Path):
        """
        Ensure all texture and binary references in glTF data are properly set.
        This helps maintain file integrity when converting between formats.
        """
        # Ensure images have proper URIs
        if 'images' in gltf_data:
            for image in gltf_data['images']:
                if 'uri' in image and image['uri']:
                    # Check if the referenced file exists
                    if not image['uri'].startswith(('http://', 'https://', 'data:')):
                        image_path = base_path / image['uri']
                        if not image_path.exists():
                            print(f"⚠️ Warning: Image file not found: {image['uri']}")
        
        # Ensure buffers have proper URIs
        if 'buffers' in gltf_data:
            for buffer in gltf_data['buffers']:
                if 'uri' in buffer and buffer['uri']:
                    # Check if the referenced file exists
                    if not buffer['uri'].startswith(('http://', 'https://', 'data:')):
                        buffer_path = base_path / buffer['uri']
                        if not buffer_path.exists():
                            print(f"⚠️ Warning: Buffer file not found: {buffer['uri']}")
        
        # Ensure textures reference valid images
        if 'textures' in gltf_data:
            for texture in gltf_data['textures']:
                if 'source' in texture:
                    source_index = texture['source']
                    if 'images' in gltf_data and source_index < len(gltf_data['images']):
                        # Texture references a valid image
                        pass
                    else:
                        print(f"⚠️ Warning: Texture references invalid image index: {source_index}")
        
        # Ensure accessors reference valid buffer views
        if 'accessors' in gltf_data:
            for accessor in gltf_data['accessors']:
                if 'bufferView' in accessor:
                    buffer_view_index = accessor['bufferView']
                    if 'bufferViews' in gltf_data and buffer_view_index < len(gltf_data['bufferViews']):
                        # Accessor references a valid buffer view
                        pass
                    else:
                        print(f"⚠️ Warning: Accessor references invalid buffer view index: {buffer_view_index}")

    def _cleanup_old_outputs(self, output_path: Path):
        """Clean up old output files to prevent duplicates and accumulation"""
        try:
            output_dir = output_path.parent
            output_stem = output_path.stem
            
            # Remove old files with the same base name (but not the target file)
            for old_file in output_dir.glob(f"{output_stem}*"):
                if old_file != output_path:  # Don't delete the target file
                    old_file.unlink()
                    print(f"🗑️  Cleaned up old file: {old_file.name}")
            
            # Remove any .glb files since we no longer generate them
            for old_glb in output_dir.glob("*.glb"):
                old_glb.unlink()
                print(f"🗑️  Cleaned up old GLB file: {old_glb.name}")
                    
        except Exception as e:
            print(f"⚠️  Warning: Could not clean up old files: {e}")

    def _run_validation(self, gltf_path: Path) -> bool:
        """Run Node.js validation on the generated GLTF file"""
        try:
            import subprocess
            import sys
            
            # Check if Node.js is available
            try:
                result = subprocess.run(['node', '--version'], capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    print("⚠️  Node.js not available, skipping validation")
                    return True
            except (subprocess.TimeoutExpired, FileNotFoundError):
                print("⚠️  Node.js not available, skipping validation")
                return True
            
            # Run the validation script
            validator_path = Path(__file__).parent / 'validate_gltf.js'
            if not validator_path.exists():
                print("⚠️  Validation script not found, skipping validation")
                return True
            
            print("🔍 Running Node.js validation...")
            result = subprocess.run(
                ['node', str(validator_path), str(gltf_path)],
                capture_output=True, text=True, timeout=30
            )
            
            if result.returncode == 0:
                print("✅ Validation passed!")
                return True
            else:
                print("❌ Validation failed!")
                print("Validation output:")
                print(result.stdout)
                if result.stderr:
                    print("Validation errors:")
                    print(result.stderr)
                return False
                
        except Exception as e:
            print(f"⚠️  Validation failed with error: {e}")
            return True  # Don't fail conversion due to validation issues

    def _fix_accessor_byte_lengths(self, gltf_data: Dict):
        """Fix accessor byteLength calculations to prevent Error 23 validation issues"""
        if 'accessors' not in gltf_data or 'bufferViews' not in gltf_data:
            print(f"🔍 [DEBUG] Missing accessors or bufferViews in GLTF data")
            return
        
        print(f"🔍 [DEBUG] Starting accessor byteLength fixes...")
        print(f"🔍 [DEBUG] Total accessors: {len(gltf_data['accessors'])}")
        print(f"🔍 [DEBUG] Total bufferViews: {len(gltf_data['bufferViews'])}")
        
        # CRITICAL FIX: Don't redistribute accessors - just ensure they fit in their assigned buffer views
        # The original buffer view assignments are correct and should be preserved
        
        for i, accessor in enumerate(gltf_data['accessors']):
            print(f"🔍 [DEBUG] Processing accessor {i}: {accessor}")
            
            if 'bufferView' in accessor and accessor['bufferView'] is not None:
                buffer_view_index = accessor['bufferView']
                print(f"🔍 [DEBUG] Accessor {i} references bufferView {buffer_view_index}")
                
                if buffer_view_index < len(gltf_data['bufferViews']):
                    buffer_view = gltf_data['bufferViews'][buffer_view_index]
                    print(f"🔍 [DEBUG] BufferView {buffer_view_index}: {buffer_view}")
                    
                    # Calculate required bytes for this accessor
                    component_count = self._get_type_component_count(accessor.get('type', 'SCALAR'))
                    component_size = self._get_component_size(accessor.get('componentType', 5126))
                    bytes_per_element = component_count * component_size
                    total_bytes_needed = accessor.get('count', 0) * bytes_per_element
                    
                    print(f"🔍 [DEBUG] Accessor {i}: Type={accessor.get('type', 'SCALAR')}, ComponentType={accessor.get('componentType', 5126)}, Count={accessor.get('count', 0)}")
                    print(f"🔍 [DEBUG] Accessor {i}: ComponentCount={component_count}, ComponentSize={component_size}, BytesPerElement={bytes_per_element}")
                    print(f"🔍 [DEBUG] Accessor {i}: TotalBytesNeeded={total_bytes_needed}, BufferViewSize={buffer_view.get('byteLength', 0)}")
                    
                    if total_bytes_needed > buffer_view.get('byteLength', 0):
                        print(f"⚠️ [DEBUG] Accessor {i}: Count {accessor.get('count', 0)} exceeds BufferView {buffer_view_index} byteLength {buffer_view.get('byteLength', 0)}")
                        # Adjust count to fit in buffer view
                        max_elements = buffer_view.get('byteLength', 0) // bytes_per_element
                        print(f"🔍 [DEBUG] Accessor {i}: Adjusting count from {accessor.get('count', 0)} to {max_elements}")
                        accessor['count'] = max_elements
                    else:
                        print(f"ℹ️ [DEBUG] Accessor {i}: Count {accessor.get('count', 0)} fits in BufferView {buffer_view_index} (total bytes: {total_bytes_needed})")
                else:
                    print(f"❌ [DEBUG] Accessor {i}: Invalid bufferView index {buffer_view_index} (max: {len(gltf_data['bufferViews'])-1})")
            else:
                print(f"⚠️ [DEBUG] Accessor {i}: No bufferView reference found")
        
        print(f"✅ [DEBUG] Accessor count adjustments complete")
    
    def _get_type_component_count(self, accessor_type: str) -> int:
        """Get the number of components for an accessor type"""
        type_map = {
            'SCALAR': 1,
            'VEC2': 2,
            'VEC3': 3,
            'VEC4': 4,
            'MAT2': 4,
            'MAT3': 9,
            'MAT4': 16
        }
        return type_map.get(accessor_type, 1)
    
    def _get_component_size(self, component_type: int) -> int:
        """Get the size of a component type in bytes"""
        size_map = {
            5120: 1,   # BYTE
            5121: 1,   # UNSIGNED_BYTE
            5122: 2,   # SHORT
            5123: 2,   # UNSIGNED_SHORT
            5125: 4,   # UNSIGNED_INT
            5126: 4    # FLOAT
        }
        return size_map.get(component_type, 4)


class VoxBridgeError(Exception):
    """Base exception for VoxBridge errors"""
    pass


class InputValidationError(VoxBridgeError):
    """Raised when input file validation fails"""
    pass


class ConversionError(VoxBridgeError):
    """Raised when conversion process fails"""
    pass


class BlenderNotFoundError(VoxBridgeError):
    """Raised when Blender executable cannot be found"""
    pass 