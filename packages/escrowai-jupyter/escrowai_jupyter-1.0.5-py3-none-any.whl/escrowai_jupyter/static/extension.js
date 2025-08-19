define([
    'base/js/namespace',
    'jquery',
    'require'
], function(Jupyter, $, require) {
    function loadCss(url) {
        var link = document.createElement("link");
        link.type = "text/css";
        link.rel = "stylesheet";
        link.href = url;
        document.getElementsByTagName("head")[0].appendChild(link);
    }

    // AnsiUp for ANSI color coding
    var AnsiUp = function() {
        this.ansi_colors = [
            [
                { color: "0, 0, 0",        class_name: "ansi-black"   },
                { color: "187, 0, 0",      class_name: "ansi-red"     },
                { color: "0, 187, 0",      class_name: "ansi-green"   },
                { color: "187, 187, 0",    class_name: "ansi-yellow"  },
                { color: "0, 0, 187",      class_name: "ansi-blue"    },
                { color: "187, 0, 187",    class_name: "ansi-magenta" },
                { color: "0, 187, 187",    class_name: "ansi-cyan"    },
                { color: "255,255,255",    class_name: "ansi-white"   }
            ],
            [
                { color: "85, 85, 85",     class_name: "ansi-bright-black"   },
                { color: "255, 85, 85",    class_name: "ansi-bright-red"     },
                { color: "0, 255, 0",      class_name: "ansi-bright-green"   },
                { color: "255, 255, 85",   class_name: "ansi-bright-yellow"  },
                { color: "85, 85, 255",    class_name: "ansi-bright-blue"    },
                { color: "255, 85, 255",   class_name: "ansi-bright-magenta" },
                { color: "85, 255, 255",   class_name: "ansi-bright-cyan"    },
                { color: "255, 255, 255",  class_name: "ansi-bright-white"   }
            ]
        ];
        
        this.ansi_to_html = function(str) {
            var self = this;
            return str.replace(/\033\[((?:\d|;)*)m/g, function(match, group1) {
                var codes = group1.split(';');
                var styles = [];
                var classes = [];
                
                for (var i = 0; i < codes.length; i++) {
                    var code = parseInt(codes[i], 10);
                    
                    if (code === 0) {
                        styles = [];
                        classes = [];
                    } else if (code === 1) {
                        styles.push('font-weight:bold');
                    } else if (code >= 30 && code <= 37) {
                        var colorIndex = code - 30;
                        classes.push(self.ansi_colors[0][colorIndex].class_name);
                    } else if (code >= 90 && code <= 97) {
                        var brightColorIndex = code - 90;
                        classes.push(self.ansi_colors[1][brightColorIndex].class_name);
                    }
                }
                
                var result = '<span';
                if (classes.length > 0) {
                    result += ' class="' + classes.join(' ') + '"';
                }
                if (styles.length > 0) {
                    result += ' style="' + styles.join(';') + '"';
                }
                result += '>';
                
                return result;
            }) + '</span>';
        };
    };
    
    var ansi_up = new AnsiUp();

    // Progress Widget class
    class ProgressWidget {
        constructor() {
            this.container = $('<div class="escrowai-progress-container"></div>');
            
            // Create the header container
            this.headerContainer = $('<div class="escrowai-header-container"></div>');
            
            // Step label
            this.stepLabel = $('<div class="escrowai-step-label">Initializing...</div>');
            
            // Progress bar
            this.progressBar = $('<div class="escrowai-progress-bar"></div>');
            this.progressFill = $('<div class="escrowai-progress-fill"></div>');
            this.progressBar.append(this.progressFill);
            
            // Details label
            this.detailsLabel = $('<div class="escrowai-details-label"></div>');
            
            // Add to header container
            this.headerContainer.append(this.stepLabel);
            this.headerContainer.append(this.progressBar);
            
            // Add to main container
            this.container.append(this.headerContainer);
            this.container.append(this.detailsLabel);
            
            // Initialize state
            this.currentStep = 'Initializing...';
            this.latestByStep = {};
            
            // Initial state
            this.updateProgress(this.currentStep, 'Preparing to start upload...', 0);
        }
        
        setErrorState(isError) {
            if (isError) {
                this.stepLabel.addClass('error');
                this.progressFill.addClass('error');
            } else {
                this.stepLabel.removeClass('error');
                this.progressFill.removeClass('error');
            }
        }
        
        scrollToBottom() {
            this.detailsLabel.scrollTop(this.detailsLabel[0].scrollHeight);
        }
        
        updateProgress(step, details, progress) {
            // Check for error state
            const isError = step === 'Error';
            this.setErrorState(isError);
            
            // Update step if changed
            if (step !== this.currentStep) {
                this.currentStep = step;
                this.stepLabel.text(step);
            }
            
            // Add new details if not empty
            if (details && details.trim()) {
                const timestamp = new Date().toLocaleTimeString();
                this.latestByStep[step] = `[${timestamp}] ${details}`;
                this.updateDisplay();
            }
            
            // Update progress bar
            const progressWidth = `${Math.min(100, Math.max(0, progress))}%`;
            this.progressFill.css('width', progressWidth);
            
            // Scroll to bottom
            this.scrollToBottom();
        }
        
        updateDisplay() {
            if (this.latestByStep[this.currentStep]) {
                const content = this.latestByStep[this.currentStep];
                const stepContent = `<div class="escrowai-output-line">${ansi_up.ansi_to_html(content)}</div>`;
                this.detailsLabel.html(stepContent);
            } else {
                this.detailsLabel.html('');
            }
        }
        
        getElement() {
            return this.container;
        }
    }

    // Modal Dialog class
    class EscrowAIModal {
        constructor() {
            this.modal = $('<div class="escrowai-modal"></div>');
            
            // Create header for dragging
            this.headerNode = $('<div class="escrowai-modal-header"></div>');
            this.titleNode = $('<div class="escrowai-modal-title">EscrowAI Upload</div>');
            this.headerNode.append(this.titleNode);
            
            // Close button
            this.closeBtn = $('<button class="escrowai-modal-close">&times;</button>');
            this.closeBtn.click(() => this.close());
            this.headerNode.append(this.closeBtn);
            
            // Body container
            this.bodyNode = $('<div class="escrowai-modal-body"></div>');
            
            // Progress widget
            this.progressWidget = new ProgressWidget();
            this.bodyNode.append(this.progressWidget.getElement());
            
            // Add elements to modal
            this.modal.append(this.headerNode);
            this.modal.append(this.bodyNode);
            
            // Dragging state
            this.isDragging = false;
            this.isMouseDown = false;
            this.xOffset = 0;
            this.yOffset = 0;
            this.mouseStartX = 0;
            this.mouseStartY = 0;
            
            // Set up drag functionality
            this.setupDrag();
            
            this.isOpen = false;
        }
        
        setupDrag() {
            this.headerNode.on('mousedown', this.dragStart.bind(this));
            $(document).on('mouseup', this.dragEnd.bind(this));
            $(document).on('mousemove', this.drag.bind(this));
        }
        
        dragStart(e) {
            // Only handle if clicking on header (not buttons)
            if ($(e.target).hasClass('escrowai-modal-close')) {
                return;
            }
            
            e.preventDefault();
            
            // Fix the position immediately to prevent jumping
            const rect = this.modal[0].getBoundingClientRect();
            
            // Check if the modal is using transform for centering
            const computedStyle = window.getComputedStyle(this.modal[0]);
            const isUsingTransform = computedStyle.transform !== 'none';
            
            if (isUsingTransform) {
                this.modal.css({
                    top: rect.top + 'px',
                    left: rect.left + 'px',
                    transform: 'none'
                });
            }
            
            // Record the initial mouse position but don't start dragging yet
            this.mouseStartX = e.clientX;
            this.mouseStartY = e.clientY;
            this.isMouseDown = true;
            
            // Calculate offset of mouse from the top-left corner of dialog
            this.xOffset = e.clientX - rect.left;
            this.yOffset = e.clientY - rect.top;
            
            console.log('Mouse down', {
                clientX: e.clientX,
                clientY: e.clientY,
                xOffset: this.xOffset,
                yOffset: this.yOffset
            });
        }
        
        dragEnd(e) {
            this.isMouseDown = false;
            
            if (!this.isDragging) return;
            
            this.isDragging = false;
            
            // Remove dragging class
            this.modal.removeClass('escrowai-dragging');
            
            console.log('Drag ended');
        }
        
        drag(e) {
            // If mouse is down but dragging hasn't started yet, check if we should start dragging
            if (this.isMouseDown && !this.isDragging) {
                // Only start dragging if mouse has moved more than 5px in any direction
                const moveX = Math.abs(e.clientX - this.mouseStartX);
                const moveY = Math.abs(e.clientY - this.mouseStartY);
                
                if (moveX > 5 || moveY > 5) {
                    this.isDragging = true;
                    // Add a class to indicate dragging is active
                    this.modal.addClass('escrowai-dragging');
                    console.log('Drag started after movement threshold');
                } else {
                    return; // Not enough movement yet
                }
            }
            
            if (!this.isDragging) return;
            
            e.preventDefault();
            
            // Direct positioning - set top/left values based on mouse position minus the initial offset
            const newLeft = e.clientX - this.xOffset;
            const newTop = e.clientY - this.yOffset;
            
            // Apply the new position
            this.modal.css({
                left: newLeft + 'px',
                top: newTop + 'px',
                transform: 'none' // Ensure transform is none
            });
            
            console.log('Dragging', { newLeft, newTop });
        }
        
        open() {
            if (this.isOpen) return;
            
            $('body').append(this.modal);
            this.isOpen = true;
        }
        
        close() {
            if (!this.isOpen) return;
            
            this.modal.remove();
            this.isOpen = false;
        }
        
        updateProgress(step, details, progress) {
            this.progressWidget.updateProgress(step, details, progress);
        }
    }

    // Load necessary CSS
    function loadExtensionCSS() {
        var cssUrl = require.toUrl('./escrowai-jupyter.css');
        loadCss(cssUrl);
    }

    // Main upload function
    function runUpload() {
        console.log('EscrowAI Extension: Command executed');
        
        // Create and show the modal dialog
        var modal = new EscrowAIModal();
        modal.open();
        
        try {
            console.log('EscrowAI Extension: Starting EventSource connection...');
            var eventSource = new EventSource('/escrowai_jupyter/run-script');
            
            eventSource.onopen = function() {
                console.log('EscrowAI Extension: EventSource connection opened');
            };
            
            eventSource.onmessage = function(event) {
                console.log('EscrowAI Extension: Received event data:', event.data);
                var data = JSON.parse(event.data);
                console.log('EscrowAI Extension: Parsed event data:', data);
                
                if (data.status === 'running') {
                    console.log('EscrowAI Extension: Processing running status update');
                    modal.updateProgress(
                        data.step || 'Processing...',
                        data.details || '',
                        data.progress || 0
                    );
                } else if (data.status === 'complete') {
                    console.log('EscrowAI Extension: Processing completion');
                    eventSource.close();
                    modal.updateProgress('Complete', 'Upload successful!', 100);
                    
                    // Show completion dialog
                    alert('Upload Complete: Successfully uploaded to EscrowAI!');
                    modal.close();
                } else if (data.status === 'error') {
                    console.error('EscrowAI Extension: Processing error:', data.error);
                    eventSource.close();
                    var errorMessage = data.error || 'Upload failed';
                    modal.updateProgress('Error', errorMessage, 0);
                    
                    // Show error dialog
                    alert('Upload Failed: ' + errorMessage);
                    modal.close();
                }
            };
            
            eventSource.onerror = function(error) {
                console.error('EscrowAI Extension: EventSource error:', error);
                eventSource.close();
                var errorMessage = 'Connection failed';
                modal.updateProgress('Error', errorMessage, 0);
                
                // Show error dialog
                alert('Upload Failed: ' + errorMessage);
                modal.close();
            };
            
        } catch (error) {
            var errorMessage = String(error);
            modal.updateProgress('Error', errorMessage, 0);
            
            // Show error dialog
            alert('Upload Failed: ' + errorMessage);
            modal.close();
        }
    }

    // Function to create menu button
    function addButton() {
        var buttonHtml = '<div class="btn-group">' +
                         '<button class="btn btn-default" title="Upload to EscrowAI">' +
                         '<i class="fa fa-upload"></i> Upload to EscrowAI</button>' +
                         '</div>';
        
        var button = $(buttonHtml);
        button.click(runUpload);
        
        $('#maintoolbar-container').append(button);
    }

    // Main extension loading function
    function load_ipython_extension() {
        console.log('EscrowAI Extension: Loading Notebook extension');
        loadExtensionCSS();
        addButton();
    }

    return {
        load_ipython_extension: load_ipython_extension
    };
}); 