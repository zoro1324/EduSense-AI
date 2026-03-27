import React, { useRef, useState } from 'react';
import { Button } from './UIPrimitives';

export const ImageUpload = ({ onImageSelect, preview }) => {
  const fileInputRef = useRef(null);
  const cameraRef = useRef(null);
  const canvasRef = useRef(null);
  const [showCamera, setShowCamera] = useState(false);
  const [cameraStream, setCameraStream] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(preview);

  const handleFileSelect = (file) => {
    if (!file.type.startsWith('image/')) {
      alert('Please select a valid image file');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert('File size must be less than 5MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      setPreviewUrl(e.target.result);
      onImageSelect(file);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const file = e.dataTransfer.files[0];
    if (file) handleFileSelect(file);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user' },
        audio: false,
      });
      setCameraStream(stream);
      setShowCamera(true);

      // Set up video stream
      setTimeout(() => {
        if (cameraRef.current) {
          cameraRef.current.srcObject = stream;
        }
      }, 100);
    } catch (error) {
      console.error('Camera access denied:', error);
      alert('Unable to access camera. Please check permissions.');
    }
  };

  const capturePhoto = () => {
    if (canvasRef.current && cameraRef.current) {
      const context = canvasRef.current.getContext('2d');
      context.drawImage(cameraRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);

      canvasRef.current.toBlob((blob) => {
        const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' });
        handleFileSelect(file);
        stopCamera();
      }, 'image/jpeg', 0.95);
    }
  };

  const stopCamera = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach((track) => track.stop());
      setCameraStream(null);
      setShowCamera(false);
    }
  };

  const clearImage = () => {
    setPreviewUrl(null);
    onImageSelect(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  return (
    <div className="space-y-2">
      {/* Preview */}
      {previewUrl && (
        <div className="relative w-full max-w-xs mx-auto">
          <img src={previewUrl} alt="Preview" className="w-full h-40 object-cover rounded-lg border border-primary/50" />
          <button
            onClick={clearImage}
            className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-red-500 text-white text-xs flex items-center justify-center hover:bg-red-600"
          >
            ✕
          </button>
        </div>
      )}

      {/* Camera View */}
      {showCamera && (
        <div className="space-y-2">
          <div className="relative w-full max-w-xs mx-auto bg-black rounded-lg overflow-hidden">
            <video
              ref={cameraRef}
              autoPlay
              playsInline
              className="w-full h-40 object-cover"
            />
            <canvas
              ref={canvasRef}
              width={320}
              height={240}
              className="hidden"
            />
          </div>
          <div className="flex gap-2 justify-center">
            <Button size="sm" onClick={capturePhoto} variant="primary">
              📸 Capture
            </Button>
            <Button size="sm" onClick={stopCamera} variant="secondary">
              Cancel
            </Button>
          </div>
        </div>
      )}

      {/* Upload Area (shown when no preview and no camera) */}
      {!previewUrl && !showCamera && (
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          className="p-6 rounded-lg border-2 border-dashed border-primary/50 bg-slate-900 text-center cursor-pointer hover:border-primary transition-colors"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={(e) => e.target.files[0] && handleFileSelect(e.target.files[0])}
            className="hidden"
          />
          <div className="space-y-2">
            <div className="text-2xl">📸</div>
            <p className="text-sm text-muted">Drag and drop an image here or click to select</p>
            <p className="text-xs text-muted">PNG, JPG, GIF up to 5MB</p>
            <div className="flex gap-2 justify-center flex-wrap">
              <Button
                size="sm"
                variant="secondary"
                onClick={() => fileInputRef.current?.click()}
              >
                📁 Choose File
              </Button>
              <Button
                size="sm"
                variant="secondary"
                onClick={startCamera}
              >
                📷 Use Camera
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
