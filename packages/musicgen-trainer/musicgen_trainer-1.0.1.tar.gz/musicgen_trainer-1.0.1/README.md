# Musicgen Trainer

Musicgen Trainer is an advanced Python module designed for music generation and synthesis. It provides tools for creating MIDI files, integrating pretrained models, and dynamically controlling parameters like tempo and key. This package is ideal for developers, musicians, and researchers looking to explore AI-driven music creation.

## Features

- **MIDI-Based Music Generation**: Generate MIDI files with customizable parameters such as tempo and key.
- **Pretrained Model Integration**: Load and use pretrained models for advanced music generation.
- **Dynamic Parameter Control**: Adjust tempo, key, and other musical attributes during generation.
- **Data Augmentation**: Enhance input sequences with noise for better generalization.
- **Error Handling and Optimization**: Robust error handling and performance improvements.

## Installation

Install the package using pip:
```bash
pip install musicgen_trainer
```

## Usage

### Import the Module
```python
from musicgen_trainer import MusicgenForConditionalGeneration
```

### Generate MIDI
```python
import torch

# Initialize the model
model = MusicgenForConditionalGeneration()

# Create a random input sequence
input_sequence = torch.randn(1, 10, 128)  # (batch_size, seq_len, input_dim)

# Generate a MIDI file
model.generate_midi(input_sequence, seq_len=100, output_path="output.mid", tempo=120, key="C")
```

### Save and Load Models
```python
# Save the model
model.save_model(model, path="musicgen_model.pth")

# Load the model
loaded_model = model.load_model(path="musicgen_model.pth")
```

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Support

For issues or questions, please contact [Your Email] or open an issue on the [GitHub repository](https://github.com/yourusername/musicgen_trainer).