let testMode = !window.DeviceOrientationEvent || window.location.hash.includes('test');
let testRotation = 0;
let usingAbsolute = false;

function updateCompass(rotation, isAbsolute) {
    const needle = document.getElementById('needle');
    const directionText = document.getElementById('direction');
    
    if (needle && directionText) {
        needle.style.transform = `translate(-50%, -100%) rotate(${rotation}deg)`;
        directionText.innerText = `Direction: ${Math.round(rotation)}° (${isAbsolute ? 'Absolute' : 'Relative'})`;
    }
}

if (testMode) {
    console.log("Running in test mode - use arrow keys to rotate");
    document.addEventListener('keydown', function(event) {
        switch(event.key) {
            case 'ArrowLeft':
                testRotation = (testRotation - 5) % 360;
                break;
            case 'ArrowRight':
                testRotation = (testRotation + 5) % 360;
                break;
        }
        updateCompass(testRotation);
    });
} else {
    if (window.DeviceOrientationEvent) {
        if (typeof DeviceOrientationEvent.requestPermission === 'function') {
            document.addEventListener('click', async function requestPermission() {
                try {
                    const permission = await DeviceOrientationEvent.requestPermission();
                    if (permission === 'granted') {
                        // Try absolute first
                        window.addEventListener("deviceorientationabsolute", function(event) {
                            console.log("Absolute event fired:", event.alpha);
                            if (event.alpha !== null) {
                                usingAbsolute = true;
                                updateCompass(event.alpha, true);
                            }
                        });
                        
                        // Only use regular orientation if absolute hasn't worked
                        setTimeout(() => {
                            if (!usingAbsolute) {
                                console.log("Falling back to regular orientation");
                                window.addEventListener("deviceorientation", function(event) {
                                    if (event.alpha !== null && !usingAbsolute) {
                                        updateCompass(event.alpha, false);
                                    }
                                });
                            }
                        }, 1000);
                    }
                } catch (error) {
                    console.error("Error requesting permission:", error);
                    document.getElementById('direction').innerText = "Permission denied";
                }
                document.removeEventListener('click', requestPermission);
            }, { once: true });
        } else {
            // Same logic for non-iOS devices
            window.addEventListener("deviceorientationabsolute", function(event) {
                console.log("Absolute event fired:", event.alpha);
                if (event.alpha !== null) {
                    usingAbsolute = true;
                    updateCompass(event.alpha, true);
                }
            });
            
            setTimeout(() => {
                if (!usingAbsolute) {
                    console.log("Falling back to regular orientation");
                    window.addEventListener("deviceorientation", function(event) {
                        if (event.alpha !== null && !usingAbsolute) {
                            updateCompass(event.alpha, false);
                        }
                    });
                }
            }, 1000);
        }
    } else {
        console.log("Device orientation not supported");
        document.getElementById('direction').innerText = "Compass not available";
    }
}