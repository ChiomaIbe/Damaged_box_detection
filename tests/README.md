# Box Detection Test Directory

This directory contains test data and results for validating the box detection model.

## Directory Structure

```
tests/
├── images/          # Test images
│   ├── damaged/     # Images of damaged boxes
│   └── undamaged/   # Images of undamaged boxes
├── videos/          # Test videos
│   ├── damaged/     # Videos containing damaged boxes
│   └── undamaged/   # Videos containing undamaged boxes
└── results/         # Detection results
    ├── images/      # Results from image detection tests
    └── videos/      # Results from video detection tests
```

## Usage Instructions

1. Add your test images:
   - Place damaged box images in `images/damaged/`
   - Place undamaged box images in `images/undamaged/`
   - Supported formats: .jpg, .jpeg, .png

2. Add your test videos:
   - Place videos with damaged boxes in `videos/damaged/`
   - Place videos with undamaged boxes in `videos/undamaged/`
   - Supported formats: .mp4, .avi

3. Results:
   - Detection results for images will be saved in `results/images/`
   - Detection results for videos will be saved in `results/videos/`

## Testing Guidelines

1. Use high-quality images and videos with good lighting
2. Include various angles and perspectives of boxes
3. Test with different types of damage (dents, tears, crushed corners, etc.)
4. Include some test cases with multiple boxes in the same frame
5. Test with different backgrounds and lighting conditions

This testing structure will help validate:
- Model accuracy in detecting boxes
- Correct classification of damaged vs undamaged boxes
- Performance with different input types (images vs videos)
- Robustness across various conditions
