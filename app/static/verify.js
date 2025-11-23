const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const verifyBtn = document.getElementById('verifyBtn');
const filePreview = document.getElementById('filePreview');
const progressContainer = document.querySelector('.progress-container');
const progressInner = document.getElementById('progressInner');
const progressText = document.getElementById('progressText');
const resultBox = document.getElementById('resultBox');
const resultMessage = document.getElementById('resultMessage');

let selectedFile = null;

// Drag & Drop
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

// File Picker
fileInput.addEventListener('change', function(e) {
  if (this.files.length) handleFile(this.files[0]);
});

uploadArea.addEventListener('click', function(e) {
  if (e.target === uploadArea || e.target.id==='uploadText') fileInput.click();
});

function handleFile(file) {
  selectedFile = file;
  filePreview.innerHTML = `<span>&#128195; ${file.name} <span style="font-size:.94em;color:#888;">(${formatSize(file.size)})</span></span>`;
  verifyBtn.disabled = false;
  hideProgress();
  hideResult();
}
function formatSize(bytes) {
  if(bytes < 1024) return `${bytes} bytes`;
  if(bytes < 1024*1024) return `${(bytes/1024).toFixed(1)} KB`;
  return `${(bytes/1024/1024).toFixed(2)} MB`;
}


function showVerificationSuccess(data) {
  resultBox.style.display = "block";
  resultMessage.innerHTML = `
    <b>Verified!</b><br>
    Document matched with record: ${data.matches[0]}
  `;
}

function showVerificationFail(data) {
  resultBox.style.display = "block";
  resultMessage.innerHTML = `
    <b>Not Verified!</b><br>
    No matching record found.<br>
  `;
}

verifyBtn.addEventListener("click", async () => {
  const form = new FormData();
  form.append("file", selectedFile);
  progressText.textContent = "Verifying...";
  const res = await fetch("/api/verify_doc", {
    method: "POST",
    body: form
  });
  const data = await res.json();
  if (data.verified) {
    showVerificationSuccess(data);
  } else {
    showVerificationFail(data);
  }
});


// // VERIFY BUTTON & ANIMATION DEMO
// verifyBtn.addEventListener('click', function() {
//   if(!selectedFile) return;
//   hideResult();
//   progressContainer.style.display = 'block';
//   progressInner.style.width = '0%';
//   progressText.textContent = "Starting verification...";

//   // Animate progress bar demo + fake result
//   let progress = 0;
//   function advance() {
//     if(progress >= 100) {
//       progressInner.style.width = '100%';
//       progressText.textContent = "Finishing...";
//       setTimeout(() => showResult(), 650);
//       return;
//     }
//     progress += Math.random()*23+12;
//     if(progress > 100) progress = 100;
//     progressInner.style.width = `${progress}%`;
//     progressText.textContent = `Verifying document... (${Math.floor(progress)}%)`;
//     setTimeout(advance, 370 + Math.random()*310);
//   }
//   advance();
// });

function hideProgress() {
  progressContainer.style.display = 'none';
  progressInner.style.width = '0%';
}

function showResult() {
  hideProgress();
  resultBox.style.display = 'block';
  setTimeout(() => resultBox.classList.add('show'), 40);
  // DEMO result
  let pass = Math.random() > 0.33;
  if(pass) {
    resultBox.style.borderLeftColor = '#36c561';
    resultBox.style.color = "#247942";
    resultMessage.innerHTML = `<b>Verified!</b> The document appears valid.<br>Type: ${selectedFile.type || selectedFile.name.split('.').pop()}<br>Name: ${selectedFile.name}`;
  } else {
    resultBox.style.borderLeftColor = '#e14809';
    resultBox.style.color = "#af1707";
    resultMessage.innerHTML = `<b>Not Verified!</b> The document could not be confirmed as valid.<br>Name: ${selectedFile.name}`;
  }
}
function hideResult() {
  resultBox.classList.remove('show');
  resultBox.style.display = 'none';
  resultMessage.innerHTML = '';
}

// ---- Camera Logic (as previously) ----
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
  // Convert to blob for verify
  canvas.toBlob(function(blob) {
    scannedImageBlob = blob;
  }, 'image/jpeg', 0.92);
};
document.getElementById('useBtn').onclick = function() {
  selectedFile = new File(
    [scannedImageBlob],
    `scanned-document-${Date.now()}.jpg`,
    {type: 'image/jpeg'}
  );
  filePreview.innerHTML = `<span>&#128247; [Scanned] ${selectedFile.name} <span style="font-size:.94em;color:#888;">(${formatSize(selectedFile.size)})</span></span>`;
  verifyBtn.disabled = false;
  hideProgress();
  hideResult();
  closeScanModal();
};
