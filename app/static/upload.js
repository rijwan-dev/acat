// Drag and drop & file preview logic
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const filePreview = document.getElementById('filePreview');

let selectedFile = null;

// Allow drag & drop
uploadArea.addEventListener('dragover', function(e) {
  e.preventDefault(); e.stopPropagation();
  uploadArea.classList.add('dragover');
});
uploadArea.addEventListener('dragleave', function(e) {
  uploadArea.classList.remove('dragover');
});
uploadArea.addEventListener('drop', function(e) {
  e.preventDefault(); e.stopPropagation();
  uploadArea.classList.remove('dragover');
  const files = e.dataTransfer.files;
  if (files.length) handleFile(files[0]);
});

// Normal file select
fileInput.addEventListener('change', function(e) {
  if (this.files.length) handleFile(this.files[0]);
});

// Clicking anywhere triggers file input
uploadArea.addEventListener('click', function(e) {
  if (e.target === uploadArea || e.target.id==='uploadText') fileInput.click();
});

function handleFile(file) {
  selectedFile = file;
  filePreview.innerHTML = `<span>&#128195; ${file.name} <span style="font-size:.94em;color:#888;">(${formatSize(file.size)})</span></span>`;
  uploadBtn.disabled = false;
}
function formatSize(bytes) {
  if(bytes < 1024) return `${bytes} bytes`;
  if(bytes < 1024*1024) return `${(bytes/1024).toFixed(1)} KB`;
  return `${(bytes/1024/1024).toFixed(2)} MB`;
}

// // Upload button action (stub)
// uploadBtn.addEventListener('click', function() {
//   if(selectedFile) {
//     alert('Uploading ' + selectedFile.name + '...\n(Demo: replace with backend upload logic!)');
//     uploadBtn.disabled = true;
//     filePreview.innerHTML = '';
//     selectedFile = null;
//   }
// });

uploadBtn.addEventListener("click", async () => {
  const form = new FormData();
  form.append("file", selectedFile);

  const res = await fetch("/api/upload_doc", {
    method: "POST",
    body: form
  });

  const data = await res.json();
  console.log(data);
  alert("Upload Completed!");
});

// Camera logic
let stream = null;
let scannedImageBlob = null;

function openScanModal() {
  document.getElementById('scanModal').style.display = 'flex';
  startCamera();
}
function closeScanModal() {
  stopCamera();
  document.getElementById('scanModal').style.display = 'none';
  document.getElementById('canvas').style.display = 'none';
  document.getElementById('video').style.display = 'block';
  document.getElementById('captureBtn').style.display = 'inline-block';
  document.getElementById('useBtn').style.display = 'none';
}
function startCamera() {
  scannedImageBlob = null;
  const video = document.getElementById('video');
  const canvas = document.getElementById('canvas');
  canvas.style.display = 'none';
  video.style.display = 'block';
  document.getElementById('captureBtn').style.display = 'inline-block';
  document.getElementById('useBtn').style.display = 'none';
  if(navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true }).then(s => {
      stream = s;
      video.srcObject = stream;
    }).catch(err => {
      alert("Unable to access camera.\n" + err);
      closeScanModal();
    });
  } else {
    alert("Camera not supported on this browser.");
    closeScanModal();
  }
}
function stopCamera() {
  if(stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
}
document.getElementById('captureBtn').onclick = function() {
  const video = document.getElementById('video');
  const canvas = document.getElementById('canvas');
  canvas.width = video.videoWidth || 320;
  canvas.height = video.videoHeight || 240;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.style.display = 'block';
  video.style.display = 'none';
  document.getElementById('captureBtn').style.display = 'none';
  document.getElementById('useBtn').style.display = 'inline-block';
  // Convert to blob for upload
  canvas.toBlob(function(blob) {
    scannedImageBlob = blob;
  }, 'image/jpeg', 0.92);
};
document.getElementById('useBtn').onclick = function() {
  // Use scannedImageBlob as a file for upload
  // For preview, set as selectedFile and preview
  selectedFile = new File(
    [scannedImageBlob],
    `scanned-document-${Date.now()}.jpg`,
    {type: 'image/jpeg'}
  );
  filePreview.innerHTML = `<span>&#128247; [Scanned] ${selectedFile.name} <span style="font-size:.94em;color:#888;">(${formatSize(selectedFile.size)})</span></span>`;
  uploadBtn.disabled = false;
  closeScanModal();
};
