let testMode = !window.DeviceOrientationEvent || window.location.hash.includes('test');
let testRotation = 0;

function updateCompass(rotation) {
    const needle = document.getElementById('needle');
    const directionText = document.getElementById('direction');
    
    if (needle && directionText) {
        needle.style.transform = `translate(-50%, -100%) rotate(${rotation}deg)`;
        directionText.innerText = `Direction: ${Math.round(rotation)}°`;
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
                        window.addEventListener("deviceorientationabsolute", function(event) {
                            if (event.alpha !== null) {
                                updateCompass(event.alpha);
                            }
                        });
                        window.addEventListener("deviceorientation", function(event) {
                            if (event.alpha !== null) {
                                updateCompass(event.alpha);
                            }
                        });
                    }
                } catch (error) {
                    console.error("Error requesting permission:", error);
                    document.getElementById('direction').innerText = "Permission denied";
                }
                document.removeEventListener('click', requestPermission);
            }, { once: true });
        } else {
            window.addEventListener("deviceorientationabsolute", function(event) {
                if (event.alpha !== null) {
                    updateCompass(event.alpha);
                }
            });
            window.addEventListener("deviceorientation", function(event) {
                if (event.alpha !== null) {
                    updateCompass(event.alpha);
                }
            });
        }
    } else {
        console.log("Device orientation not supported");
        document.getElementById('direction').innerText = "Compass not available";
    }
}