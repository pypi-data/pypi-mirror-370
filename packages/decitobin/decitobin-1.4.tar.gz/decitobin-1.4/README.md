decitobin 🧒🔢
decitobin is a versatile Python tool that converts between number systems and text — now with a web-style user interface and enhanced features.

Whether you're converting decimal to binary, exploring ASCII encoding, or transforming hexadecimal strings, decitobin offers an interactive and beginner-friendly experience.

🌟 Features
🧠 Support for multiple conversions:
- |----------------|
- | Decimal → Binary|  
- | Binary → Decimal | 
- | ASCII → Binary  |
- | Binary → ASCII | 
- | Hex → Binary | 
- | Binary → Hex |
- | Decimal → Hex |
- | Hex → Decimal |
- |-------------|
🖥️ Graphical interface with dropdown selection (Tkinter-based)

🚀 Instant results with detailed formatting

📦 Easy to install and run on any platform

💻 Installation
```sh
pip install decitobin
```
🎮 Launching the App
Run the converter using:
```sh
python -m decitobin
```
Or run your own launcher script using:

```python
import decitobin
print(decitobin.dec2bin("12")) # Output: 1100
print(decitobin.ascii2bin("A")) # Output: 01000001
print(decitobin.bin2hex(1011)) # Output: A
print(decitobin.dec2hex(16)) # Output: F
```
✨ Example Conversions
| Input	| Mode	| Output |
|-------|-------|-------|
| 13	| Decimal → Binary	| 1101 |
| 1101	| Binary → Decimal	| 13 |
| Hi	| ASCII → Binary	| 01001000 01101001 |
| 01001000 01101001	| Binary → ASCII	| Hi |
| F0	| Hex → Binary	| 11110000 |
| 11110000	| Binary → Hex	| F0 |
|---------|-------|-------|
📄 License
Licensed under the MIT License.