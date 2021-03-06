/*
 *  Copyright (c) 2015 The WebRTC project authors. All Rights Reserved.
 *
 *  Use of this source code is governed by a BSD-style license
 *  that can be found in the LICENSE file in the root of the source
 *  tree.
 */

'use strict';

// Put variables in global scope to make them available to the browser console.
const video = document.querySelector('video');
const videoSelect = document.querySelector('select#videoSource');
const selectors = [videoSelect];

function gotDevices(deviceInfos) {
  // Handles being called several times to update labels. Preserve values.
  const values = selectors.map(select => select.value);
  selectors.forEach(select => {
    while (select.firstChild) {
      select.removeChild(select.firstChild);
    }
  });
  for (let i = 0; i !== deviceInfos.length; ++i) {
    const deviceInfo = deviceInfos[i];
    const option = document.createElement('option');
    option.value = deviceInfo.deviceId;
    if (deviceInfo.kind === 'videoinput') {
      option.text = deviceInfo.label || `camera ${videoSelect.length + 1}`;
      videoSelect.appendChild(option);
    } else {
      console.log('Some other kind of source/device: ', deviceInfo);
    }
  }
  selectors.forEach((select, selectorIndex) => {
    if (Array.prototype.slice.call(select.childNodes).some(n => n.value === values[selectorIndex])) {
      select.value = values[selectorIndex];
    }
  });
}

navigator.mediaDevices.enumerateDevices().then(gotDevices).catch(handleError);


const canvas = window.canvas = document.querySelector('canvas');
canvas.width = 480;
canvas.height = 360;

const recognizeBtn = document.getElementById('recognize');

const takeSnapshot = document.getElementById('takeSnapshot');
takeSnapshot.onclick = function() {
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0, canvas.width, canvas.height);
  prepareImg();
  canvas.scrollIntoView();
};


function gotStream(stream) {
  window.stream = stream; // make stream available to browser console
  video.srcObject = stream;
  return navigator.mediaDevices.enumerateDevices();
}


function start() {
  if (window.stream) {
    window.stream.getTracks().forEach(track => {
      track.stop();
    });
  }
  const videoSource = videoSelect.value;
  const constraints = {
    audio: false,
    video: {deviceId: videoSource ? {exact: videoSource} : undefined}
  };
  navigator.mediaDevices.getUserMedia(constraints).then(gotStream).then(gotDevices).catch(handleError);
}


function prepareImg() {
	var canvasData = canvas.toDataURL("image/png");
   	document.getElementById('image_input').value = canvasData;
}


const toggleVideo = document.getElementById('toggleVideo');
toggleVideo.onclick = function() {
  video.srcObject.getTracks().forEach(track => {
      if (track.enabled === true) {
        track.enabled = false;
        toggleVideo.innerHTML = "<img width='20px' margin='1px' src='https://cdn0.iconfinder.com/data/icons/video-conference-1/24/Disable-Camera_2-512.png'>";
      } else {
        track.enabled = true;
        toggleVideo.innerHTML = "<img width='20px' margin='1px' src='https://cdn3.iconfinder.com/data/icons/video-meeting-2/24/enable_camera_video_meeting_conference_online-512.png'>";
      }
  });
};

const clearSnap = document.getElementById('clearSnap');
clearSnap.onclick = function() {
  canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
  video.scrollIntoView();

}

function handleError(error) {
  document.getElementById('error').innerHTML = `Error: ${error.message}`;
  console.log('navigator.MediaDevices.getUserMedia error: ', error.message, error.name);
  takeSnapshot.disabled = true;
  recognizeBtn.disabled = true;
  toggleVideo.disabled  = true;
}

videoSelect.onchange = start;

start();



