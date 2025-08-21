import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

function fitCameraToObject(camera, box, controls) {
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());

    const maxSize = Math.max(size.x, size.y, size.z);
    const fitHeightDistance = maxSize / (2 * Math.atan(Math.PI * camera.fov / 360));
    const fitWidthDistance = fitHeightDistance / camera.aspect;
    const distance = Math.max(fitHeightDistance, fitWidthDistance) * 7;

    camera.position.copy(center);
    camera.position.z += distance; // Adjust this to position camera correctly


    camera.near = distance / 100;
    camera.far = distance * 100;
    camera.updateProjectionMatrix();
    
    controls.target.copy(center);

    controls.update();

  
    //controls.target.y -= 1; // Optionally adjust the target downward
    //controls.update();
    //camera.lookAt(center);
    //camera.rotation.x -= Math.PI / 20; // Optionally rotate the camera slightly
}

function extractAndDivide(str) {
    var numericPart = parseFloat(str.replace('%', '')); // Remove '%' and convert to float
    return numericPart / 100; // Divide by 100
}


let activeModels = []; 

export function toggleAnimations(shouldAnimate) {
    activeModels.forEach(modelObj => {
        if (modelObj.mixer) {
            // You can also add individual control here if needed
            modelObj.mixer.timeScale = shouldAnimate ? 1 : 0; // 0 stops, 1 plays
        }
    });
}


export function import3DModel(modelDataURL,width){

   
    const w = extractAndDivide(width)
    console.log('Three.js version:', THREE.REVISION);
     //Scene
    //const scene = new Scene();
    const scene = new THREE.Scene();
    const clock = new THREE.Clock();

    // Increase the intensity of the ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 1); // set intensity to 1
    scene.add(ambientLight);
    
    // Increase the intensity of the directional light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 2); // set intensity to 2 for stronger light
    directionalLight.position.set(1, 2, 4);
    scene.add(directionalLight);
    
    // Optionally, add another light source if you want more illumination in your scene
    const pointLight = new THREE.PointLight(0xffffff, 1.5, 100); // intensity is 1.5 and distance is 100
    pointLight.position.set(-2, 3, -5); // adjust the position as per your needs
    scene.add(pointLight);
    
     //Camera
     const camera = new THREE.PerspectiveCamera(50, 16/9*w, 0.1, 1000);
     camera.position.z = 5;
    
     //Renderer
     const renderer = new THREE.WebGLRenderer({ alpha: true });
     renderer.setClearColor(0x000000, 0);  // 
     renderer.setSize(window.innerWidth, window.innerHeight);
    
    
     const controls = new OrbitControls(camera, renderer.domElement);
    
     const arrayBuffer = modelDataURL.data ? new Uint8Array(modelDataURL.data) : new Uint8Array(modelDataURL);


     const blob        = new Blob([arrayBuffer], { type: 'model/gltf-binary' });
     const blobURL     = URL.createObjectURL(blob);

     
     // Now you can use the three.js loader with the blob URL
     const loader = new GLTFLoader();
     let mixer; // Animation mixer
    
     
     loader.load(blobURL, function(obj) {
     scene.add( obj.scene );
   

      // Animation handling
      if (obj.animations && obj.animations.length > 0) {
        mixer = new THREE.AnimationMixer(obj.scene);
        obj.animations.forEach((clip) => {
            mixer.clipAction(clip).play();
        });
      }

     console.log('test')
     //Calculate bounding box and center   
     var box = new THREE.Box3().setFromObject( obj.scene );
     const center = box.getCenter(new THREE.Vector3());
    
     //Adjust camera target
     controls.target.copy(center);
     //controls.update(); 
     camera.lookAt(center);

     fitCameraToObject(camera, box, controls);
    
      // Add the model and its mixer to the activeModels array
      activeModels.push({ model: obj.scene, mixer: mixer });
      
     })
    
    
     function animate() {
        requestAnimationFrame(animate);

          // Update the mixer on each frame
          if (mixer) {
            const delta = clock.getDelta(); // Assuming you've defined a THREE.Clock
            mixer.update(delta);
        }

        controls.update();
        renderer.render(scene, camera);
     }
    
     animate();
    
    
    
    return renderer.domElement
    
    }
    