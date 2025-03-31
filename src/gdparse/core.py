import base64
import zlib
from typing import Dict, List, Any, Optional

# Constants
TRIGGERS_IDS = [
    22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 55, 56, 57, 58, 59,
    104, 105, 221, 899, 901,
    1006, 1007, 1049, 1268, 1346, 1347, 1520, 1585, 1595, 1611, 1612,
    1613, 1615, 1616, 1811, 1812, 1814, 1815, 1816, 1817, 1818, 1819,
    1912, 1913, 1914, 1915, 1916, 1917, 1932, 1934, 1935, 2015, 2016,
    2062, 2066, 2067, 2068, 2899, 2900, 2901, 2903, 2904, 2905, 2907,
    2909, 2910, 2911, 2912, 2913, 2914, 2915, 2916, 2917, 2919, 2920,
    2921, 2922, 2923, 2924, 2925, 2999, 3006, 3007, 3008, 3009, 3010,
    3011, 3012, 3013, 3014, 3015, 3016, 3017, 3018, 3019, 3020, 3021,
    3022, 3023, 3024, 3029, 3030, 3031, 3032, 3033, 3600, 3602, 3603,
    3604, 3605, 3606, 3607, 3608, 3609, 3612, 3613, 3614, 3615, 3617,
    3618, 3619, 3620, 3640, 3641, 3642, 3643, 3660, 3661, 3662
]

class GDLevelCrypto:
    """
    Handles the decryption and encryption of GD level strings.
    """
    @staticmethod
    def decrypt(encrypted_string: str) -> str:
        """Decrypts a GD level string."""
        # 1. Парсим строку в словарь
        items = encrypted_string.split(':')
        parsed_level = {}
        for i in range(0, len(items), 2):
            if i + 1 < len(items):
                parsed_level[items[i]] = items[i + 1]
            else:
                parsed_level[items[i]] = ''
        
        # 2. Извлекаем зашифрованные данные
        level_data = parsed_level.get("4", "")
        
        # 3. Расшифровываем
        try:
            base64_decoded = base64.urlsafe_b64decode(level_data.encode())
            decompressed = zlib.decompress(base64_decoded, 15 | 32)
            return decompressed.decode()
        except Exception as e:
            raise ValueError(f"Failed to decode level data: {e}")

    @staticmethod
    def encrypt(level_data: str, is_official_level_music: bool = False) -> str:
        """Encrypts level data to GD format."""
        if is_official_level_music:
            level_data = 'H4sIAAAAAAAAA' + level_data
            
        compressed = zlib.compress(level_data.encode())
        base64_encoded = base64.urlsafe_b64encode(compressed).decode()
        return base64_encoded

class LevelObject:
    """
    Represents an individual object within a GD level.
    """
    def __init__(self, obj_string: str) -> None:
        self.properties: Dict[int, Any] = {}
        self.parse_object(obj_string)

    def parse_object(self, obj_string: str) -> None:
        """
        Parses the object string into key-value properties.
        """
        pairs = obj_string.split(',')
        for i in range(0, len(pairs) - 1, 2):
            try:
                key = int(pairs[i])
                value_str = pairs[i + 1]
                value = self._convert_value(value_str)
                self.properties[key] = value
            except (ValueError, IndexError):
                continue  # Skip invalid pairs

    @classmethod
    def create_block(cls, block_id: int, x: float, y: float, **properties) -> 'LevelObject':
        """
        Creates a new block with specified parameters.
        
        Args:
            block_id: The ID of the block type
            x: X position
            y: Y position
            **properties: Additional properties for the block
            
        Returns:
            LevelObject: A new block object
        """
        # Basic properties that most blocks need
        base_properties = {
            1: block_id,  # Object ID
            2: x,         # X position
            3: y,         # Y position
        }
        
        # Update with any additional properties
        base_properties.update(properties)
        
        # Convert to string format
        properties_str = ','.join(f"{k},{v}" for k, v in base_properties.items())
        return cls(properties_str)

    @staticmethod
    def _convert_value(value: str) -> Any:
        """
        Converts the string value to an appropriate type.
        """
        try:
            if '.' in value:
                return float(value)
            return int(value)
        except ValueError:
            return value

    def is_trigger(self) -> bool:
        """
        Determines if the object is a trigger based on its ID.
        """
        return self.properties.get(1) in TRIGGERS_IDS

    def __str__(self) -> str:
        return (f"Object ID: {self.properties.get(1, 'Unknown')}, "
                f"Position: ({self.properties.get(2, '?')}, {self.properties.get(3, '?')}). "
                f"Properties: {self.properties}")

class GDLevel:
    """
    Represents a GD Level with headers, colors, and objects.
    Provides methods for parsing and serializing the level.
    """
    def __init__(self, level_string: str, ignore_triggers: bool = True) -> None:
        self.ignore_triggers = ignore_triggers
        self.headers: Dict[str, Any] = {}
        self.colors: Dict[int, Dict[str, Any]] = {}
        self.objects: List[LevelObject] = []
        self.version: str = self.detect_version(level_string)
        self.parse_level(level_string)

    @classmethod
    def create_empty(cls, version: str = "2.0+") -> 'GDLevel':
        """
        Создает новый пустой уровень с базовыми настройками.
        
        Args:
            name: Название уровня
            version: Версия формата GD ("1.0", "1.9", или "2.0+")
            
        Returns:
            Новый экземпляр GDLevel
        """
        # Создаем экземпляр без вызова __init__
        level = cls.__new__(cls)
        
        # Инициализируем базовые атрибуты
        level.ignore_triggers = False
        level.version = version
        level.headers = {}
        level.colors = {}
        level.objects = []

        level.headers = {}
        
        # Добавляем заголовки, специфичные для версии
        if version == "2.0+":
            level.headers["kS38"] = ""
        
        # Инициализируем базовые цвета
        if version == "2.0+":
            # Базовый цвет фона
            level.colors[1] = {
                'r': 125,
                'g': 125,
                'b': 125,
                'blending': False,
                'opacity': 1.0
            }
            # Базовый цвет земли
            level.colors[2] = {
                'r': 75,
                'g': 75,
                'b': 75,
                'blending': False,
                'opacity': 1.0
            }
        
        return level

    @staticmethod
    def detect_version(level_string: str) -> str:
        """
        Detects the version of the level based on specific keys.
        """
        if "kS38" in level_string:
            return "2.0+"
        elif "kS29" in level_string:
            return "1.9"
        else:
            return "1.0"

    def parse_level(self, level_string: str) -> None:
        """
        Parses the entire level string into headers, colors, and objects.
        """
        parts = level_string.split(';')
        if len(parts) < 2:
            raise ValueError("Invalid level string format.")

        # Parse headers
        header_parts = parts[0].split(',')
        for i in range(0, len(header_parts) - 1, 2):
            key = header_parts[i]
            value = header_parts[i + 1]
            self.parse_header_value(key, value)

        # Parse colors based on version
        if self.version == "1.0":
            self.parse_colors_1_0()
        elif self.version == "2.0+":
            color_string = self.headers.get("kS38", "")
            self.parse_colors_2_0(color_string)

        # Parse objects
        for obj_string in parts[1:-1]:
            if obj_string:
                level_object = LevelObject(obj_string)
                if self.ignore_triggers and level_object.is_trigger():
                    continue
                self.objects.append(level_object)

    def parse_header_value(self, key: str, value: str) -> None:
        """
        Parses and stores a single header key-value pair.
        """
        if key == "kS38" and self.version == "2.0+":
            self.parse_colors_2_0(value)
        else:
            try:
                if '.' in value:
                    self.headers[key] = float(value)
                else:
                    self.headers[key] = int(value)
            except ValueError:
                self.headers[key] = value

    def parse_colors_1_0(self) -> None:
        """
        Parses color information for version 1.0 levels.
        """
        color_groups = {
            'background': (1, 2, 3),
            'ground': (4, 5, 6),
            'line': (7, 8, 9),
            'object': (10, 11, 12),
            'player2': (13, 14, 15)
        }

        for name, (r_key, g_key, b_key) in color_groups.items():
            r = self.headers.get(f'kS{r_key}')
            g = self.headers.get(f'kS{g_key}')
            b = self.headers.get(f'kS{b_key}')
            if r is not None and g is not None and b is not None:
                self.colors[r_key] = {
                    'r': r,
                    'g': g,
                    'b': b,
                    'blending': False,
                    'opacity': 1.0
                }

    def parse_colors_2_0(self, color_string: str) -> None:
        """
        Parses color information for version 2.0+ levels.
        """
        color_channels = color_string.split('|')
        for channel in color_channels:
            if not channel:
                continue

            properties = {}
            pairs = channel.split('_')
            for i in range(0, len(pairs) - 1, 2):
                try:
                    properties[int(pairs[i])] = pairs[i + 1]
                except (ValueError, IndexError):
                    continue

            channel_id = int(properties.get(6, 0))
            if channel_id == 0:
                continue  # Skip if channel_id is not set

            self.colors[channel_id] = {
                'r': int(properties.get(1, 0)),
                'g': int(properties.get(2, 0)),
                'b': int(properties.get(3, 0)),
                'blending': bool(int(properties.get(5, 0))),
                'opacity': float(properties.get(7, 1)),
            }

    def add_object(self, level_object: LevelObject) -> None:
        """
        Adds a new object to the level.
        """
        if not (self.ignore_triggers and level_object.is_trigger()):
            self.objects.append(level_object)

    def remove_object(self, obj_id: int) -> bool:
        """
        Removes an object by its ID. Returns True if removed, else False.
        """
        for i, obj in enumerate(self.objects):
            if obj.properties.get(1) == obj_id:
                del self.objects[i]
                return True
        return False

    def get_object_by_id(self, obj_id: int) -> Optional[LevelObject]:
        """
        Retrieves an object by its ID.
        """
        for obj in self.objects:
            if obj.properties.get(1) == obj_id:
                return obj
        return None

    def serialize(self) -> str:
        """
        Serializes the level back into its string format.
        """
        # Serialize headers
        header_parts = []
        for key, value in self.headers.items():
            header_parts.extend([key, str(value)])
        header_str = ",".join(header_parts)

        # Serialize colors
        if self.version == "2.0+":
            color_strs = []
            for channel_id, color in self.colors.items():
                parts = [
                    f"1_{color['r']}",
                    f"2_{color['g']}",
                    f"3_{color['b']}",
                    f"5_{int(color['blending'])}",
                    f"6_{channel_id}",
                    f"7_{color['opacity']}"
                ]
                color_strs.append("_".join(parts))
            colors_serialized = "|".join(color_strs)
            header_str += f",kS38,{colors_serialized}"
        elif self.version == "1.0":
            for channel_id, color in self.colors.items():
                self.headers[f'kS{channel_id}'] = color['r']
                self.headers[f'kS{channel_id + 1}'] = color['g']
                self.headers[f'kS{channel_id + 2}'] = color['b']
            # Re-serialize headers
            header_parts = []
            for key, value in self.headers.items():
                header_parts.extend([key, str(value)])
            header_str = ",".join(header_parts)

        # Serialize objects
        object_strs = [",".join([str(k) for pair in obj.properties.items() for k in pair]) for obj in self.objects]
        objects_serialized = ";".join(object_strs)

        # Combine all parts
        level_str = f"{header_str};{objects_serialized};"
        return level_str

    def reset_colors(self) -> None:
        """
        Resets all color information to default values.
        Removes all custom colors and color channels.
        """
        # Clear color dictionary
        self.colors.clear()

        # Remove color-related headers
        if self.version == "2.0+":
            if "kS38" in self.headers:
                del self.headers["kS38"]
        else:
            # For version 1.0, remove all kS1-kS15 headers
            for i in range(1, 16):
                key = f"kS{i}"
                if key in self.headers:
                    del self.headers[key]

    def __str__(self) -> str:
        version_str = f"GD Level (Version {self.version})\n"
        header_str = "Headers:\n" + "\n".join(f"  {k}: {v}" for k, v in self.headers.items())
        colors_str = "Colors:\n" + "\n".join(
            f"  Channel {k}: RGB({v['r']}, {v['g']}, {v['b']}) "
            f"Blend: {v['blending']} Opacity: {v['opacity']}" for k, v in self.colors.items()
        )
        objects_str = f"Objects ({len(self.objects)})" # + "\n".join(f"  {obj}" for obj in self.objects)
        return f"{version_str}\n{header_str}\n\n{colors_str}\n\n{objects_str}"

# Example Usage
if __name__ == "__main__":
    encrypted_level = "1:114027874:2:Placeholder:3::4:H4sIAAAAAAAACq1TyQ3DMAxbyAVEHTmQV2foABogK3T4WmaeCdqifYSMQ4qSDGR_2NKQLqkJjbTUiARISuJHzxtySohIzolEFCwpuSSeyBEh-lkEfo9YTyPKw4KPQjSr_izoqyvp598z_PJOuA76ym_Wict1vryX6V9BZ0u1_Q5rUhSkieStI9_ngXroPGEpethKbSBzhnD3gVQhNNGltCkdOjeUXUgg6SBllDLFqBk142jOMGeYB8upmdHpJI5v7Fd_WtE6CMcWrNNjXHD4Tlu17n2jWQGiP9sLnB56Wa8DAAA=:5:2:6:237923769:8:0:9:0:10:21:12:0:13:22:14:-2:17::43:0:25::18:0:19:0:42:0:45:4:15:0:30:0:31:0:28:1 hour:29:1 minute:35:0:36::37:0:38:0:39:1:46:31:47:0:40:0:57:682:27:Aw==#018ee041b2ee5de52963da287055a4e3274d01b1#b31d3fe59b458bcddaac801f5106a4e4f2df9567"
    
    try:
        # Расшифровка уровня
        decrypted_data = GDLevelCrypto.decrypt(encrypted_level)
        print("Decrypted Level Data:")
        print(decrypted_data)
        
        # Parse the decrypted data into a GDLevel object
        gd_level = GDLevel(decrypted_data)
        print("\nParsed GD Level:")
        print(gd_level)
        
        # Modify an object (example: change the position of the first object)
        if gd_level.objects:
            first_object = gd_level.objects[0]
            print("\nOriginal First Object:")
            print(first_object)
            first_object.properties[2] = 150  # Change X position
            first_object.properties[3] = 250  # Change Y position
            print("Modified First Object:")
            print(first_object)

            # New objects
            for i in range(100):
                new_block = LevelObject.create_block(
                    block_id=1,        # Regular platform
                    x=15+30 * i,       # X position
                    y=200,             # Y position
                )
                gd_level.add_object(new_block)
        
        # Serialize the level back to string
        serialized_level = gd_level.serialize()
        print("\nSerialized Level:")
        print(serialized_level)
        
        # Encrypt the serialized level
        encrypted_level_new = GDLevelCrypto.encrypt(serialized_level, is_official_level_music=False)
        print("\nRe-encrypted Level String:")
        print(encrypted_level_new)
        
    except Exception as e:
        print(f"Error: {e}")