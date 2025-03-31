# GD Parse

A Python library for parsing, modifying, and serializing Geometry Dash level data. It allows you to decrypt level strings obtained from the game or servers, interact with level components like headers, colors, and objects in a structured way, and then serialize and re-encrypt them.

## Installation

```bash
pip install gdparse
```

## Core Features

*   **Decrypt** Geometry Dash level strings.
*   **Parse** decrypted level data into structured Python objects (`GDLevel`, `LevelObject`).
*   **Access and Modify** level headers, color channels, and individual objects.
*   **Add** new objects or **Remove** existing ones programmatically.
*   **Create** new, empty levels with default settings.
*   **Serialize** `GDLevel` objects back into the GD string format.
*   **Encrypt** level data strings for use in Geometry Dash.
*   Automatically **Detect** level format versions (1.0, 1.9, 2.0+).
*   Optionally **Filter out Triggers** during parsing for simpler analysis or modification.

## Usage Examples

### 1. Decrypting and Parsing a Level

```python
from gdparse import GDLevelCrypto, GDLevel, LevelObject

# Example encrypted level string (replace with your actual level string)
encrypted_level_string = "1:114027874:2:Placeholder:3::4:H4sIAAAAAAAACq1TyQ3DMAxbyAVEHTmQV2foABogK3T4WmaeCdqifYSMQ4qSDGR_2NKQLqkJjbTUiARISuJHzxtySohIzolEFCwpuSSeyBEh-lkEfo9YTyPKw4KPQjSr_izoqyvp598z_PJOuA76ym_Wict1vryX6V9BZ0u1_Q5rUhSkieStI9_ngXroPGEpethKbSBzhnD3gVQhNNGltCkdOjeUXUgg6SBllDLFqBk142jOMGeYB8upmdHpJI5v7Fd_WtE6CMcWrNNjXHD4Tlu17n2jWQGiP9sLnB56Wa8DAAA=:5:2:6:237923769:8:0:9:0:10:21:12:0:13:22:14:-2:17::43:0:25::18:0:19:0:42:0:45:4:15:0:30:0:31:0:28:1 hour:29:1 minute:35:0:36::37:0:38:0:39:1:46:31:47:0:40:0:57:682:27:Aw==#018ee041b2ee5de52963da287055a4e3274d01b1#b31d3fe59b458bcddaac801f5106a4e4f2df9567"

try:
    # Decrypt the level string
    decrypted_data = GDLevelCrypto.decrypt(encrypted_level_string)
    print("--- Decrypted Level Data ---")
    # print(decrypted_data) # Usually very long, print sparingly

    # Parse the decrypted data into a GDLevel object
    # Set ignore_triggers=False if you want to include triggers
    gd_level = GDLevel(decrypted_data, ignore_triggers=True)

    print("\n--- Parsed GD Level Info ---")
    print(f"Level Version Detected: {gd_level.version}")
    print(f"Number of Objects (excluding triggers): {len(gd_level.objects)}")
    # print(gd_level) # Print full details if needed

except ValueError as e:
    print(f"Error processing level: {e}")

```

### 2. Accessing and Modifying Level Data

```python
# Assuming 'gd_level' is the parsed GDLevel object from the previous example

if gd_level:
    # Access Headers
    print("\n--- Level Headers ---")
    # Print a few common headers if they exist
    print(f"Background ID: {gd_level.headers.get('k2')}")
    print(f"Ground ID: {gd_level.headers.get('k3')}")
    print(f"Music ID: {gd_level.headers.get('k4')}")
    # print("All Headers:", gd_level.headers)

    # Access Colors (structure depends on version)
    print("\n--- Level Colors ---")
    if gd_level.version == "2.0+":
        bg_color = gd_level.colors.get(1) # Channel 1 is usually BG
        if bg_color:
            print(f"Background Color (Ch 1): RGB({bg_color['r']}, {bg_color['g']}, {bg_color['b']}) Opacity: {bg_color['opacity']}")
    # print("All Colors:", gd_level.colors)

    # Access and Modify Objects
    if gd_level.objects:
        first_object = gd_level.objects[0]
        print("\n--- Modifying First Object ---")
        print(f"Original First Object Position: ({first_object.properties.get(2)}, {first_object.properties.get(3)})")

        # Change its position (key 2 is X, key 3 is Y)
        first_object.properties[2] = first_object.properties.get(2, 0) + 60 # Move 60 units right
        first_object.properties[3] = 105 # Set Y to 105

        print(f"Modified First Object Position: ({first_object.properties.get(2)}, {first_object.properties.get(3)})")

    # Add a new object
    print("\n--- Adding New Object ---")
    new_block = LevelObject.create_block(
        block_id=21,  # Spike block ID
        x=150,
        y=105
    )
    gd_level.add_object(new_block)
    print(f"Added new object: {new_block}")
    print(f"New total object count: {len(gd_level.objects)}")

```

### 3. Serializing and Encrypting a Level

```python
# Assuming 'gd_level' is the potentially modified GDLevel object

if gd_level:
    try:
        # Serialize the GDLevel object back into a string
        serialized_level_data = gd_level.serialize()
        print("\n--- Serialized Level Data ---")
        # print(serialized_level_data) # Can be very long

        # Encrypt the serialized data
        # Set is_official_level_music appropriately if needed (rarely true for user levels)
        re_encrypted_string = GDLevelCrypto.encrypt(serialized_level_data, is_official_level_music=False)
        print("\n--- Re-encrypted Level String ---")
        print(re_encrypted_string)

    except Exception as e:
        print(f"Error serializing or encrypting: {e}")

```

### 4. Creating an Empty Level

```python
from gdparse import GDLevel, LevelObject, GDLevelCrypto

# Create a new empty level (defaults to version 2.0+)
empty_level = GDLevel.create_empty(version="2.0+")

print("--- Created Empty Level ---")
print(f"Version: {empty_level.version}")
print(f"Initial Objects: {len(empty_level.objects)}")
print(f"Initial Colors: {empty_level.colors}")

# Add a starting block
start_block = LevelObject.create_block(block_id=1, x=0, y=75)
empty_level.add_object(start_block)
print(f"Objects after adding start block: {len(empty_level.objects)}")

# Serialize and encrypt the new level
serialized_empty = empty_level.serialize()
encrypted_empty = GDLevelCrypto.encrypt(serialized_empty)

print("\n--- Encrypted Empty Level String ---")
print(encrypted_empty)
```

---

**Disclaimer:** This library code and README were generated with the assistance of an AI because the author is lazy. Use at your own risk.