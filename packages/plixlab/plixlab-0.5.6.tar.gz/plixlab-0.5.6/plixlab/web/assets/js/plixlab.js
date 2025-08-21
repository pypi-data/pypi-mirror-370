import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

function fitCameraToObject(camera, box, controls, padding = 6) {
    const size = box.getSize(new THREE.Vector3());
    const center = box.getCenter(new THREE.Vector3());

    const maxSize = Math.max(size.x, size.y, size.z);
    const fitHeightDistance = maxSize / (2 * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2));
    const fitWidthDistance = fitHeightDistance / camera.aspect;

    const distance = Math.max(fitHeightDistance, fitWidthDistance) * padding;

    // Position camera
    camera.position.copy(center);
    camera.position.z += distance;

    camera.near = distance / 100;
    camera.far = distance * 100;
    camera.updateProjectionMatrix();

    // Update controls
    controls.target.copy(center);
    controls.update();
}

function extractAndDivide(str) {
    return parseFloat(str.replace('%', '')) / 100;
}

export function import3DModel(modelDataURL, width, onLoadCallback) {
    const w = extractAndDivide(width);

    // Scene + clock
    const scene = new THREE.Scene();
    const clock = new THREE.Clock();

    // Lights
    const lights = [
        new THREE.AmbientLight(0xffffff, 1),
        new THREE.DirectionalLight(0xffffff, 2),
        new THREE.PointLight(0xffffff, 1.5, 100),
    ];
    lights[1].position.set(1, 2, 4);
    lights[2].position.set(-2, 3, -5);
    scene.add(...lights);

    // Camera
    const camera = new THREE.PerspectiveCamera(50, 16 / 9 * w, 0.1, 1000);
    camera.position.z = 5;

    // Renderer
    const renderer = new THREE.WebGLRenderer({
        alpha: true,
        preserveDrawingBuffer: true,
    });
    renderer.setClearColor(0x000000, 0);
    renderer.setSize(window.innerWidth, window.innerHeight);

    // Controls
    const controls = new OrbitControls(camera, renderer.domElement);
    renderer.domElement.threeControls = controls;

    // Model loader
    const arrayBuffer = modelDataURL.data
        ? new Uint8Array(modelDataURL.data)
        : new Uint8Array(modelDataURL);

    const blobURL = URL.createObjectURL(new Blob([arrayBuffer], { type: 'model/gltf-binary' }));
    const loader = new GLTFLoader();

    let mixer;
    loader.load(blobURL, (obj) => {
        scene.add(obj.scene);

        // Setup animations if present
        if (obj.animations?.length) {
            mixer = new THREE.AnimationMixer(obj.scene);
            obj.animations.forEach((clip) => mixer.clipAction(clip).play());
        }

        // Fit camera to model
        const box = new THREE.Box3().setFromObject(obj.scene);
        fitCameraToObject(camera, box, controls);

        if (onLoadCallback) onLoadCallback();
    });

    // Animation loop
    function animate() {
        requestAnimationFrame(animate);

        if (mixer) mixer.update(clock.getDelta());
        controls.update();
        renderer.render(scene, camera);
    }
    animate();

    // Store refs for thumbnails
    const canvas = renderer.domElement;
    canvas.threeRenderer = renderer;
    canvas.threeScene = scene;
    canvas.threeCamera = camera;
    canvas.threeControls = controls;

    return canvas;
}



function apply_style(element, style) {
    for (let styleProp in style) {
        let cssValue = style[styleProp];
        if (typeof cssValue === 'number' && ['fontSize', 'width', 'height', 'top', 'right', 'bottom', 'left'].includes(styleProp)) {
            cssValue += 'px';
        }
        element.style[styleProp] = cssValue;
    }
}

//Embed function
const modal = document.getElementById("embed-modal");
const overlay = document.getElementById("embed-overlay");
const closeBtn = document.getElementById("embed-close");
const checkbox = document.getElementById("carousel-toggle");
const embedCheckbox = document.getElementById("embed-toggle");
const linkInput = document.getElementById("embed-link");
const embedTextarea = document.getElementById("embed-code");

document.getElementById("embed").addEventListener("click", () => {
  updateEmbed();
  modal.style.display = "block";
});

overlay.addEventListener("click", () => modal.style.display = "none");
closeBtn.addEventListener("click", () => modal.style.display = "none");

function updateEmbed() {
  const url = new URL(window.location.href);

  if (checkbox.checked) {
    url.searchParams.set("carousel", "True");
  } else {
    url.searchParams.delete("carousel");
  }

  if (embedCheckbox.checked) {
    url.searchParams.set("embed", "True");
  } else {
    url.searchParams.delete("embed");
  }

  const link = url.toString();

  linkInput.value = link;
  embedTextarea.value = `
<div style="position: relative; width: 100%; max-width: 800px; height: 450px; margin: auto;">
  <iframe
    src="${link}"
    title="Plix"
    style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;"
    allowfullscreen
  ></iframe>
</div>`.trim();
}
checkbox.addEventListener("change", updateEmbed);
embedCheckbox.addEventListener("change", updateEmbed);

// Copy to clipboard with Font Awesome feedback
document.querySelectorAll("[data-copy]").forEach(btn => {
  btn.addEventListener("click", async () => {
    const selector = btn.getAttribute("data-copy");
    const el = document.querySelector(selector);
    await navigator.clipboard.writeText(el.value);
    btn.innerHTML = '<i class="fa-solid fa-check"></i>';
    setTimeout(() => {
      btn.innerHTML = '<i class="fa-regular fa-copy"></i>';
    }, 1000);
  });
});




function update_markdown(element, field, value) {
    //Update Markdown
    // Build markdown formatter--
    const markedInstance = marked.setOptions({
        langPrefix: 'hljs language-',
        highlight: function (code, lang) {
            const language = hljs.getLanguage(lang) ? lang : 'plaintext';
            return hljs.highlight(code, { language }).value;
        }
    });

    if (field === 'text') {
        element.innerHTML = markedInstance(value);
    }

    if (field === 'style') {
        
        value['pointerEvents']= 'none'; 
        value['user-select']= "none";
        value['contenteditable']= "false" 
        value['tabindex']="-1"
        apply_style(element, value);

        if (value.alignItems === 'center' && value.justifyContent === 'center') {
            let paragraphs = element.querySelectorAll('p');
            paragraphs.forEach(p => {
                p.style.textAlign = 'center';
                p.style.lineHeight = 1.5;
            });
        }
    }

    if (field === 'fontsize') {
        function set_fontsize(element, newFontsize) {
            let outer_element = element.parentElement;

            function setDynamicFontSize() {
                let fontSize = outer_element.offsetHeight * newFontsize;
                element.style.fontSize = fontSize + 'px';
            }

            // Use ResizeObserver to observe size changes on outer_element
            const ro = new ResizeObserver(() => {
                setDynamicFontSize();
            });

            // Disconnect the existing observer if it exists
            if (element.ResizeObserver) {
                element.ResizeObserver.disconnect();
            }

            ro.observe(outer_element);

            element.ResizeObserver = ro;

            setDynamicFontSize(); // Initial call
        }

        set_fontsize(element, value);
    }
}


function render_slide(slide_id, slide) {
    let element = document.createElement('div');
    element.className = 'slide';
    element.id = slide_id;
    element.style.backgroundColor = slide.style.backgroundColor;
    element.dataset.animation = JSON.stringify(slide.animation);
    


    document.getElementById('slide-container').appendChild(element);

    for (const key in slide['children']) {
        add_component(key, slide['children'][key], element);
    }
}




export async function render_slides(slides) {

    //Delete current slides
    const slides_to_remove = document.querySelectorAll('.slide');
    slides_to_remove.forEach(slide => slide.remove());

    // Create all slides
    for (const slide in slides) {
        render_slide(slide, slides[slide]);
    }

    //Initialize datastore
    window.dataStore = {'active_slide': 0, 'index': 0, 'mode': 'presentation'};

    // Set initial slide visibility - show first slide, hide others
    const allSlides = document.querySelectorAll(".slide");
    allSlides.forEach((slide, index) => {
        slide.style.visibility = index === 0 ? 'visible' : 'hidden';
    });
    
    // Handle MathJax typesetting after content is loaded
    if (window.MathJax && window.MathJax.typesetPromise) {
        try {
            await MathJax.typesetPromise();
        } catch (error) {
            console.warn('MathJax typeset failed:', error);
        }
    } else if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
        // Wait for MathJax to be ready if it's still loading
        try {
            await window.MathJax.startup.promise;
            if (window.MathJax.typesetPromise) {
                await MathJax.typesetPromise();
            }
        } catch (error) {
            console.warn('MathJax initialization failed:', error);
        }
    }

    // Now populate sidebar after ALL slides are fully rendered
    populateSidebar();
 
}

window.render_slides = render_slides;


function add_component(id, data, outer_element) {
    if (data.type === 'Markdown') {
        const element = document.createElement('div');
        element.className = 'markdownComponent COMPONENT_MARKDOWN';
        element.id = id;
        outer_element.appendChild(element);
        update_markdown(element, 'text', data.text);
        update_markdown(element, 'style', data.style);
        update_markdown(element, 'fontsize', data.fontsize);
    }

    if (data.type === 'Img') {
        // Create the element (assuming it's an img tag)
        const element = document.createElement('img');
        element.className = 'COMPONENT_IMG';
        element.id = id;
        outer_element.appendChild(element);

        if (typeof data.src === 'string' && data.src.startsWith("https")) {
            fetch(data.src)
                .then(response => response.arrayBuffer()) // Handle binary data
                .then(arrayBuffer => element.src = arrayBuffer)
                .catch(error => console.error('Error fetching the model:', error));
        } else {
            //local
            const arrayBuffer = data.src.data
                ? new Uint8Array(data.src.data).buffer
                : new Uint8Array(data.src).buffer;
            const blob = new Blob([arrayBuffer], { type: 'image/png' }); // Replace 'image/png' with the correct MIME type if needed
            const blobURL = URL.createObjectURL(blob);
            element.src = blobURL;
        }
       
        apply_style(element, data.style);
    }

    if (data.type === 'model3D') {
        function add_model(src) {
            // Create a Promise that resolves when the 3D model is loaded
            let resolveModelLoaded;
            const modelLoadedPromise = new Promise((resolve) => {
                resolveModelLoaded = resolve;
            });

            const element = import3DModel(src, data.style.width, () => {
                // This callback is called when the model is fully loaded
                resolveModelLoaded();
            });
            
            element.id = id;
            outer_element.appendChild(element);
            element.className = 'COMPONENT_MODEL3D';
            apply_style(element, data.style);

            // Store the Promise on the element
            element.modelLoadedPromise = modelLoadedPromise;

       element.generateThumbnail = async function() {
    await element.modelLoadedPromise;
    
    // Ensure we have the Three.js references
    if (element.threeRenderer && element.threeScene && element.threeCamera) {
        // Force a render to ensure current state
        element.threeRenderer.render(element.threeScene, element.threeCamera);
        
        return new Promise((resolve) => {
            requestAnimationFrame(() => {
                resolve(element.toDataURL('image/png'));
            });
        });
    }
    
    return null;
};

        }

        if (typeof data.src === 'string' && data.src.startsWith("https")) {
            fetch(data.src)
                .then(response => response.arrayBuffer()) // Handle binary data
                .then(arrayBuffer => add_model(arrayBuffer))
                .catch(error => console.error('Error fetching the model:', error));
        } else {
            add_model(data.src);
        }
    }

    if (data.type === 'Iframe') {
        const element = document.createElement('iframe');
        element.setAttribute('frameborder', '1');
        element.src = data.src;
        element.id = id;
        element.className = 'COMPONENT_IFRAME';
        apply_style(element, data.style);
        outer_element.appendChild(element);
    }


    if (data.type === 'Plotly') {
        const config = {
            responsive: true,
            scrollZoom: true,
            staticPlot: false
        };
        const element = document.createElement('div');
        element.id = id;
    
        apply_style(element, data.style);
      
        element.className = 'COMPONENT_PLOTLY'; 
        outer_element.appendChild(element);
    
        const figure = JSON.parse(data.figure);

        // Create a Promise that resolves when the plot is rendered
        element.plotlyLoadedPromise = new Promise((resolve) => {
            element.resolvePlotlyLoaded = resolve;
        });

        // Render the plot and resolve Promise when complete
        Plotly.react(element, figure.data, figure.layout, config).then(() => {
            // Resolve the Promise when Plotly is fully rendered
            element.resolvePlotlyLoaded();
        });
      
        // Store thumbnail generation function for sidebar use
        element.generateThumbnail = async function() {
            try {
                // Wait for Plotly to be fully rendered using Promise
                await element.plotlyLoadedPromise;
                
                const url = await Plotly.toImage(element, {format: 'png'});
                return url;
            } catch (error) {
                console.error("Error generating Plotly thumbnail:", error);
                return null;
            }
        };
    }

    if (data.type === 'Bokeh') {
        const element = document.createElement('div');
        element.id = id;
        outer_element.appendChild(element);
        element.className = 'COMPONENT_BOKEH';
        apply_style(element, data.style);

        try {
            Bokeh.embed.embed_item(data.graph, element);
        } catch (error) {
            console.error("Error embedding Bokeh plot:", error);
        }

        // Add thumbnail generation using Bokeh's native export
        element.generateThumbnail = async function() {
            try {
                // Wait for Bokeh to populate the index
                const waitForBokehIndex = () => {
                    return new Promise((resolve) => {
                        const checkIndex = () => {
                            const plotViews = Object.values(Bokeh.index);
                            if (plotViews.length > 0) {
                                resolve(plotViews);
                            }
                        };
                        
                        checkIndex();
                        
                        const observer = new MutationObserver(() => {
                            checkIndex();
                            if (Object.values(Bokeh.index).length > 0) {
                                observer.disconnect();
                            }
                        });
                        
                        observer.observe(element, { childList: true, subtree: true });
                    });
                };
                
                const plotViews = await waitForBokehIndex();
                if (plotViews.length === 0) return null;
                
                const targetPlotView = plotViews.find(view => 
                    view.el && element.contains(view.el)
                ) || plotViews[0];
                
                if (!targetPlotView) return null;
                
                const blob = await targetPlotView.export().to_blob();
                
                return new Promise((resolve) => {
                    const reader = new FileReader();
                    reader.onloadend = () => resolve(reader.result);
                    reader.readAsDataURL(blob);
                });
                
            } catch (error) {
                return null;
            }
        };

    }

    if (data.type === 'molecule') {
        // Create a new div element
        const element = document.createElement("div");
       
        element.id = id;
        element.className = 'COMPONENT_MOLECULE';
    
        outer_element.appendChild(element);
    
        apply_style(element, data.style);
      
        var viewer = $3Dmol.createViewer(id, {
           defaultcolors: $3Dmol.rasmolElementColors,
           backgroundColor: data.backgroundColor
        });

        // Create a Promise that resolves when the molecule is loaded
        element.moleculeLoadedPromise = new Promise((resolve) => {
            element.resolveMoleculeLoaded = resolve;
        });

        // Store thumbnail generation function immediately (before download completes)
        element.generateThumbnail = async function() {
            try {
                // Wait for molecule to be fully loaded using Promise
                await element.moleculeLoadedPromise;
                
                // Get canvas and generate thumbnail using toDataURL
                const canvas = viewer.getCanvas ? viewer.getCanvas() : element.querySelector('canvas');
                if (canvas) {
                    return canvas.toDataURL('image/png');
                }
                
                return null;
            } catch (error) {
                console.error("Error generating molecule thumbnail:", error);
                return null;
            }
        };

        $3Dmol.download("pdb:" + data.structure, viewer,{}, function () {
            viewer.setBackgroundColor(data.backgroundColor);
            viewer.setViewStyle({style:"outline"});
            viewer.setStyle({},{cartoon:{ color: 'spectrum'}});
            viewer.render();
            
            // Resolve the Promise when molecule is fully loaded
            element.resolveMoleculeLoaded();
        });
    }
}



function populateSidebar() {
    const sidebarSlides = document.getElementById('sidebar-slides');
    const slides = document.querySelectorAll("#slide-container .slide");
    
    // Clear existing sidebar content
    sidebarSlides.innerHTML = '';
    
    slides.forEach((slide, index) => {
        const sidebarSlide = document.createElement('div');
        sidebarSlide.className = 'sidebar-slide';
        if (index === window.dataStore.active_slide) {
            sidebarSlide.classList.add('active');
        }
        
        // Create a simple copy of the slide for thumbnail
        const slideClone = slide.cloneNode(true);
        
        // Remove the 'slide' class to prevent it from being affected by navigation
        slideClone.classList.remove('slide');
        slideClone.classList.add('sidebar-thumbnail');
        
        // Give it a unique ID to prevent conflicts
        slideClone.id = slide.id + '-thumbnail';
        
        // Make thumbnail always visible and scaled down
        slideClone.style.visibility = 'visible !important';
        slideClone.style.position = 'relative';
        slideClone.style.transform = 'scale(0.2)';
        slideClone.style.transformOrigin = 'top left';
        slideClone.style.width = '500%';
        slideClone.style.height = '500%';
        slideClone.style.pointerEvents = 'none';
        slideClone.style.border = 'none';
        slideClone.style.overflow = 'hidden';
        slideClone.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.5) !important';
        slideClone.style.borderRadius = '6px !important';
        slideClone.style.backgroundColor = 'rgba(50, 50, 50, 0.8)'; // Dark background to see content
        
        // Update IDs to avoid conflicts with main slides and handle thumbnails
        const thumbnailComponents = slideClone.querySelectorAll('*');
        thumbnailComponents.forEach(async component => {
            if (component.id) {
                // Check if the original element has a generateThumbnail method first
                const originalElement = slide.querySelector(`#${component.id}`);
                
                if (originalElement && originalElement.generateThumbnail) {
                    // Create thumbnail image to replace any component with generateThumbnail method
                    const thumbnailImg = document.createElement('img');
                    thumbnailImg.style.width = '100%';
                    thumbnailImg.style.height = '100%';
                    thumbnailImg.style.objectFit = 'contain';
                    thumbnailImg.style.objectPosition = 'center';
                    
                    // Generate thumbnail immediately
                    originalElement.generateThumbnail().then(url => {
                        if (url) {
                            thumbnailImg.src = url;
                        }
                    }).catch(error => {
                        console.error("Failed to generate thumbnail:", error);
                    });
                    
                    // Replace the component with the thumbnail image
                    component.parentNode.replaceChild(thumbnailImg, component);
                }
                
                // Only change ID after thumbnail processing is done
                component.id = component.id + '-thumbnail';
            }
        });
        
        sidebarSlide.appendChild(slideClone);
        
        // Add click handler for navigation
        sidebarSlide.onclick = () => {
            navigateToSlideFromSidebar(index);
        };
        
        sidebarSlides.appendChild(sidebarSlide);
    });
    
    // Force content height to ensure scrolling works
    const totalHeight = slides.length * 130; // 120px per slide + gap
    if (totalHeight > window.innerHeight - 30) {
        sidebarSlides.style.height = totalHeight + 'px';
    }
}

// Function to navigate from sidebar thumbnail to presentation mode
function navigateToSlideFromSidebar(slideIndex) {
    // Update active slide
    window.dataStore.active_slide = slideIndex;
    window.dataStore.index = 0;
    
    // Hide all slides except the selected one in the main container
    const slides = document.querySelectorAll("#slide-container .slide");
    slides.forEach((slide, index) => {
        if (index !== slideIndex) {
            slide.style.visibility = 'hidden';
        } else {
            slide.style.visibility = 'visible';
        }
    });
    

    // Update sidebar active state (only border, don't change visibility)
    const sidebarSlides = document.querySelectorAll('.sidebar-slide');
    sidebarSlides.forEach((sidebarSlide, index) => {
        if (index === slideIndex) {
            sidebarSlide.classList.add('active');
        } else {
            sidebarSlide.classList.remove('active');
        }
    });
}

// Function called by increment/decrementSlide
function updateSidebarSelection(slideIndex) {
    const sidebarSlides = document.querySelectorAll('.sidebar-slide');
    sidebarSlides.forEach((sidebarSlide, index) => {
        if (index === slideIndex) {
            sidebarSlide.classList.add('active');
        } else {
            sidebarSlide.classList.remove('active');
        }
    });
}


window.addEventListener('load', async function () {

    function setupSwipeNavigation() {
        let touchStartX = 0;
        let touchEndX = 0;
        const threshold = 50;
    
        function handleGesture() {
            const deltaX = touchEndX - touchStartX;
            if (Math.abs(deltaX) < threshold) return;
    
            if (deltaX > 0) {
                if (window.dataStore.mode === 'presentation') {
                    decrementSlide();
                } else if (window.dataStore.mode === 'full') {
                    decrementEvent();
                }
            } else {
                if (window.dataStore.mode === 'presentation') {
                    incrementSlide();
                } else if (window.dataStore.mode === 'full') {
                    incrementEvent();
                }
            }
        }
    
        const swipeTarget = document.getElementById('slide-container');
    
        swipeTarget.addEventListener("touchstart", (e) => {
            if (e.target.closest('.COMPONENT_PLOTLY')) return;
            touchStartX = e.changedTouches[0].screenX;
        }, { passive: false });  // not passive
    
        swipeTarget.addEventListener("touchend", (e) => {
            if (e.target.closest('.COMPONENT_PLOTLY')) return;
            touchEndX = e.changedTouches[0].screenX;
            handleGesture();
        }, { passive: false });  // not passive
    }

    setupSwipeNavigation();


    //Keys
    document.addEventListener('keydown', function (event) {
        if (window.dataStore.mode == 'presentation') {
            if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
                incrementSlide();
            } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
                decrementSlide();
            }
        }

        if (window.dataStore.mode == 'full') {
            if (event.key === 'ArrowRight' || event.key === 'ArrowDown') {
                incrementEvent();
            } else if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') {
                decrementEvent();
            }
        }

        if (event.key === 'Escape') {
            // Exit fullscreen mode if active
            if (document.fullscreenElement && window.dataStore.mode === 'full') {
                document.exitFullscreen();
            }
        }
    });



    function incrementEvent() {

       
        const NSlideEvents = JSON.parse(document.querySelectorAll(".slide")[window.dataStore.active_slide].dataset.animation).length;

        //console.log(document.querySelectorAll(".slide")[window.dataStore.active_slide].dataset.animation)
        if (window.dataStore.index < NSlideEvents - 1) {
            window.dataStore.index += 1;
        } else {
            incrementSlide();
        }

        updateEventVisibility();
    }

    function decrementEvent() {
        if (window.dataStore.index > 0) {
            window.dataStore.index -= 1;
        } else {
            decrementSlide();
        }

        updateEventVisibility();
    }

    function decrementSlide() {
        const slides = document.querySelectorAll(".slide"); // Select all slides
        const totalSlides = slides.length;
    
        const currentSlide = slides[window.dataStore.active_slide];
        currentSlide.style.visibility = 'hidden'; // Use 'hidden' to hide it

        const prev_index = (window.dataStore.active_slide - 1 + totalSlides) % totalSlides;

        const prevSlide = slides[prev_index];
        prevSlide.style.visibility = 'visible';

        window.dataStore.active_slide = prev_index;
        window.dataStore.index = 0;
        const NSlideEvents = JSON.parse(document.querySelectorAll(".slide")[window.dataStore.active_slide].dataset.animation).length;
        window.dataStore.index = NSlideEvents - 1;

        // Update sidebar
        updateSidebarSelection(prev_index);
    }
    

    function incrementSlide() {
        const slides = document.querySelectorAll(".slide"); 
        const totalSlides = slides.length;
      
        const currentSlide = slides[window.dataStore.active_slide];
        const newSlide_index = (window.dataStore.active_slide + 1) % totalSlides;
        const newSlide = slides[newSlide_index];
       
        currentSlide.style.visibility = 'hidden';
        newSlide.style.visibility = 'visible';

        window.dataStore.active_slide = newSlide_index
        window.dataStore.index = 0;

        // Update sidebar
        updateSidebarSelection(newSlide_index);
    }




const urlParams = new URLSearchParams(window.location.search);
const isCarousel = urlParams.get('carousel') === 'True';
const isEmbed = urlParams.get('embed') === 'True';

// Handle embed mode
if (isEmbed) {
    // Hide only the sidebar, keep the control buttons
    const sidebar = document.getElementById('slide-sidebar');
    
    if (sidebar) sidebar.style.display = 'none';
    
    // Make slide container fill entire viewport while maintaining 16:9 ratio
    const slideContainer = document.getElementById('slide-container');
    if (slideContainer) {
        slideContainer.classList.add('embed-mode');
    }
}

let carouselInterval;

if (isCarousel) {
    
    const interval = 3000; // ms between slides

    carouselInterval = setInterval(() => {
        incrementSlide();  // you handle wraparound inside this
    }, interval);

    const stopCarousel = () => clearInterval(carouselInterval);

    document.addEventListener('keydown', stopCarousel, { once: true });
    document.addEventListener('click', stopCarousel, { once: true });
    document.addEventListener('touchstart', stopCarousel, { once: true });
}


    function updateEventVisibility() {
       
        const slide = document.querySelectorAll(".slide")[window.dataStore.active_slide]

        const animation = JSON.parse(slide.dataset.animation)[window.dataStore.index];

    
        for (let key in animation) {
           
            let element = document.getElementById(slide.id + '_' + key);
           
            if (animation[key]) {
                element.style.visibility = 'hidden';

                if (element.className === 'PLOTLY') {
                    element.hidden = true;
                }
            } else {
                element.style.visibility = 'inherit';
                if (element.className === 'PLOTLY') {
                    element.hidden = false;
                }
            }
        }
    }


    function fullScreen() {
        const slideContainer = document.getElementById('slide-container');
        const slides = document.querySelectorAll(".slide");

        // Set mode to full
        window.dataStore.mode = 'full';

        // Add fullscreen mode styling immediately
        slideContainer.classList.add('fullscreen-mode');
        
        // Show only the active slide
        slides.forEach((slide, index) => {
            if (index === window.dataStore.active_slide) {
                slide.style.visibility = 'visible';
            } else {
                slide.style.visibility = 'hidden';
            }
            slide.style.border = 'none';
        });

        // Reset event index and update visibility
        window.dataStore.index = 0;
        updateEventVisibility();

        // Try to request browser fullscreen (optional)
        if (slideContainer.requestFullscreen) {
            slideContainer.requestFullscreen().catch(error => {
                console.log('Browser fullscreen not available or denied:', error);
            });
        }

        // Handle fullscreen exit
        document.addEventListener('fullscreenchange', function() {
            if (!document.fullscreenElement) {
                slideContainer.classList.remove('fullscreen-mode');
                window.dataStore.mode = 'presentation';

                // Show the active slide in normal presentation mode
                slides.forEach((slide, index) => {
                    slide.style.visibility = (index === window.dataStore.active_slide) ? 'visible' : 'hidden';
                    slide.style.border = 'none';
                });
            }
        });
    }

    // Uncomment if you have a full-screen button
     document.getElementById('full-screen').addEventListener('click', function() {
        fullScreen();
     });
});