# Entity Image Upload Feature

## Overview
The Expert Review Dashboard now supports image upload and management for entities. This feature allows experts to attach visual references to entities, making the review process more comprehensive and intuitive.

## Features

### ✅ Image Upload
- **Supported Formats**: JPEG, PNG, GIF, WebP
- **File Size Limit**: 5MB maximum
- **Automatic Processing**: Images are automatically resized and optimized
- **Unique Naming**: Each uploaded image gets a unique filename to prevent conflicts

### ✅ Image Display
- **Entity Table**: Thumbnail images (40x40px) displayed in dedicated column
- **Edit Modal**: Full-size image preview with upload/delete controls
- **Full-Size View**: Click thumbnails to view images in full-size modal
- **Placeholder**: Visual placeholder for entities without images

### ✅ Image Management
- **Upload**: Drag-and-drop or click to select image files
- **Replace**: Upload new image to replace existing one
- **Delete**: Remove images with confirmation
- **Automatic Cleanup**: Deleted images are removed from storage

## Usage Instructions

### 1. Uploading Images

#### Via Entity Edit Modal:
1. Click "Edit" button for any entity in the entity list
2. In the edit modal, find the "Entity Image" section
3. Click "Choose File" or drag an image file to the upload area
4. Click "Upload Image" button
5. Image preview will appear immediately

#### Supported File Types:
- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

### 2. Viewing Images

#### In Entity Table:
- Images appear as 40x40px thumbnails in the "Image" column
- Entities without images show a placeholder icon
- Click any thumbnail to view full-size image

#### In Edit Modal:
- Full-size image preview (max 200px height)
- Upload and delete controls
- Real-time preview updates

### 3. Managing Images

#### Replacing Images:
1. Open entity edit modal
2. Upload new image (automatically replaces old one)
3. Old image file is automatically deleted

#### Deleting Images:
1. Open entity edit modal
2. Click "Delete Image" button
3. Confirm deletion
4. Image is removed from entity and storage

## API Endpoints

### Upload Image
```http
POST /api/expert-review/entities/{entity_id}/upload-image
Content-Type: multipart/form-data

file: [image file]
```

### Get Image Info
```http
GET /api/expert-review/entities/{entity_id}/image
```

### Delete Image
```http
DELETE /api/expert-review/entities/{entity_id}/image
```

## Technical Implementation

### Backend Components
- **Image Storage**: `frontend/static/uploads/entity_images/`
- **API Endpoints**: `backend/api/expert_review_api.py`
- **Data Model**: Added `image_url` field to all entity types
- **File Management**: Automatic cleanup and unique naming

### Frontend Components
- **Upload Interface**: File input with drag-and-drop support
- **Image Display**: Responsive thumbnails and full-size modals
- **JavaScript**: Upload, delete, and preview functionality
- **CSS Styling**: Responsive design with hover effects

### File Organization
```
frontend/static/uploads/entity_images/
├── {entity_id}_{unique_hash}.jpg
├── {entity_id}_{unique_hash}.png
└── ...
```

## Testing

### Run Image Upload Tests
```bash
python test_image_upload.py
```

### Test Coverage
- ✅ Image upload with various formats
- ✅ File size validation
- ✅ Image retrieval and display
- ✅ Image deletion and cleanup
- ✅ Entity list integration
- ✅ Edit modal integration

## Security Considerations

### File Validation
- **Type Checking**: Only image MIME types allowed
- **Size Limits**: 5MB maximum file size
- **Extension Validation**: File extensions verified
- **Content Validation**: Basic image format validation

### Storage Security
- **Unique Filenames**: Prevents filename conflicts and guessing
- **Isolated Directory**: Images stored in dedicated upload directory
- **Access Control**: Images served through static file handler

## Performance Optimization

### Image Processing
- **Thumbnail Generation**: Automatic thumbnail creation for table display
- **Lazy Loading**: Images loaded on demand
- **Caching**: Browser caching for uploaded images
- **Compression**: Automatic image optimization

### Storage Management
- **Cleanup**: Automatic deletion of replaced/removed images
- **Organization**: Structured file naming and directory organization
- **Monitoring**: File size and count monitoring

## Troubleshooting

### Common Issues

#### Upload Fails
- Check file size (must be < 5MB)
- Verify file format (JPEG, PNG, GIF, WebP only)
- Ensure entity exists in database
- Check server permissions for upload directory

#### Images Not Displaying
- Verify image URL in entity data
- Check static file serving configuration
- Ensure upload directory exists and is accessible
- Check browser console for errors

#### Performance Issues
- Monitor upload directory size
- Implement image compression if needed
- Consider CDN for large deployments
- Regular cleanup of orphaned images

### Debug Commands
```bash
# Check upload directory
ls -la frontend/static/uploads/entity_images/

# Test API endpoints
curl -X GET http://localhost:9000/api/expert-review/entities/{id}/image

# Verify static file serving
curl -X GET http://localhost:9000/static/uploads/entity_images/test.jpg
```

## Future Enhancements

### Planned Features
- **Bulk Image Upload**: Upload multiple images at once
- **Image Gallery**: View all entity images in gallery format
- **Image Annotations**: Add annotations and markup to images
- **Image Search**: Search entities by image content
- **Image Versioning**: Keep history of image changes

### Integration Opportunities
- **PDF Extraction**: Automatically extract images from PDF documents
- **Schematic Analysis**: Link images to schematic diagrams
- **AI Analysis**: Automatic image content analysis and tagging
- **Export Features**: Include images in ontology exports

## Conclusion

The image upload feature significantly enhances the Expert Review Dashboard by providing visual context for entities. This makes the review process more intuitive and comprehensive, especially for complex medical device components and systems.

The implementation follows best practices for security, performance, and user experience, providing a solid foundation for future enhancements.