import os
import numpy as np
import cv2

def create_test_dataset():
    for split in ['train', 'val', 'test']:
        os.makedirs(f'data/dataset/images/{split}', exist_ok=True)
        os.makedirs(f'data/dataset/labels/{split}', exist_ok=True)
    
    print("Creating test dataset...")
    
    for split, count in [('train', 15), ('val', 3), ('test', 2)]:
        for i in range(count):
            img = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
            img_path = f'data/dataset/images/{split}/image_{i:03d}.jpg'
            cv2.imwrite(img_path, img)
            
            labels = [
                f"0 {np.random.rand():.3f} {np.random.rand():.3f} 0.2 0.3\n",
                f"1 {np.random.rand():.3f} {np.random.rand():.3f} 0.3 0.4\n"
            ]
            label_path = f'data/dataset/labels/{split}/image_{i:03d}.txt'
            with open(label_path, 'w') as f:
                f.writelines(labels)
            
            print(f"  Created {split}/image_{i:03d}")
    
    print("✓ Test dataset created!")

if __name__ == '__main__':
    create_test_dataset()