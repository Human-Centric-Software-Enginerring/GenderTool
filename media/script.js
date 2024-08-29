// (function() {
//     const vscode = acquireVsCodeApi();

//     const hoverInfo = {
//         primaryContribution: {
//             navigator: "It can be a good idea to switch roles freely so that both you and your partner can have a fair say in the code.",
//             driver: "It can be a good idea to switch roles freely so that both you and your partner can have a fair say in the code."
//         },
//         communicationStyle: {
//             nonvisual: "Make sure to listen and acknowledge what your partner says by responding verbally as well.",
//             visual: "Try to watch your partner's body language to see how they feel and understand them better."
//         },
//         partnerTrying: {
//             working: "Continue focusing on the task, but remember to be friendly with your partner to build connection.",
//             friendly: "Continue being friendly but remember to focus on the task at hand."
//         }
//     };

//     const whyLinks = {
//         primaryContribution: {
//             navigator: "https://www.jstor.org/stable/26196132?seq=1",
//             driver: "https://www.jstor.org/stable/26196132?seq=1"
//         },
//         communicationStyle: {
//             visual: "https://ieeexplore.ieee.org/document/9568912",
//             nonvisual: "https://academic.oup.com/joc/article-abstract/52/3/522/4110025?redirectedFrom=fulltext"
//         },
//         partnerTrying: {
//             working: "https://dl.acm.org/doi/abs/10.1145/3498326",
//             friendly: "https://dl.acm.org/doi/abs/10.1145/3498326"
//         }
//     };

//     // Info popups
//     document.querySelectorAll('.info-icon').forEach(icon => {
//         icon.addEventListener('click', function() {
//             const popupType = this.id.replace('Info', '');
//             showPopup(popupType);
//         });
//     });

//     function showPopup(type) {
//         const popup = document.getElementById('popup');
//         const popupText = document.getElementById('popupText');
//         const popupIcon = document.querySelector('.popup-icon');
//         const whyLink = document.querySelector('.why-link');
//         const toggle = document.getElementById(`${type}Toggle`);

//         let state;
//         switch(type) {
//             case 'primaryContribution':
//                 state = toggle.checked ? 'driver' : 'navigator';
//                 break;
//             case 'communicationStyle':
//                 state = toggle.checked ? 'visual' : 'nonvisual';
//                 break;
//             case 'partnerTrying':
//                 state = toggle.checked ? 'working' : 'friendly';
//                 break;
//         }

//         let text = hoverInfo[type][state];
//         popupText.textContent = text;
//         popupIcon.innerHTML = '💡';
//         whyLink.style.color = '#ff0000';
//         whyLink.dataset.link = whyLinks[type][state];
//         popup.style.display = 'block';
//     }

//     document.querySelector('.close-btn').addEventListener('click', function() {
//         document.getElementById('popup').style.display = 'none';
//     });

//     // Why link click handler
//     document.querySelector('.why-link').addEventListener('click', function() {
//         const link = this.dataset.link;
//         if (link) {
//             vscode.postMessage({
//                 command: 'openLink',
//                 link: link
//             });
//         }
//     });

//     // Toggle switches
//     document.querySelectorAll('.toggle-input').forEach(toggle => {
//         toggle.addEventListener('change', function() {
//             const type = this.id.replace('Toggle', '');
//             const value = this.checked ? 'ON' : 'OFF';
//             vscode.postMessage({
//                 command: 'updateStat',
//                 type: type,
//                 value: value
//             });
//         });
//     });

//     // Handle messages from the extension
//     window.addEventListener('message', event => {
//         const message = event.data;
//         switch (message.command) {
//             case 'updateStats':
//                 document.getElementById('linesOfCode').textContent = message.linesOfCode;
//                 document.getElementById('interruptionCount').textContent = message.interruptionCount;
//                 document.getElementById('primaryContributionToggle').checked = message.primaryContribution === 'Driver';
//                 document.getElementById('communicationStyleToggle').checked = message.communicationStyle === 'Visual';
//                 document.getElementById('partnerTryingToggle').checked = message.partnerTrying === 'Friendly';
//                 break;
//         }
//     });
//     document.getElementById('runTest2Btn').addEventListener('click', () => {
//         const sessionId = document.getElementById('sessionIdInput').value;
//         console.log(`Sending sessionId to extension: ${sessionId}`);
//         vscode.postMessage({
//             command: 'runTest2',
//             sessionId: sessionId
//         });
//     });
// })();
(function () {
    const vscode = acquireVsCodeApi();

    // Debugging output
    console.log('script.js loaded');

    // Information for tooltips
    const hoverInfo = {
        primaryContribution: {
            navigator: "It can be a good idea to switch roles freely so that both you and your partner can have a fair say in the code.",
            driver: "It can be a good idea to switch roles freely so that both you and your partner can have a fair say in the code."
        },
        communicationStyle: {
            nonvisual: "Make sure to listen and acknowledge what your partner says by responding verbally as well.",
            visual: "Try to watch your partner's body language to see how they feel and understand them better."
        },
        partnerTrying: {
            working: "Continue focusing on the task, but remember to be friendly with your partner to build connection.",
            friendly: "Continue being friendly but remember to focus on the task at hand."
        }
    };

    // Links for "Why?" buttons
    const whyLinks = {
        primaryContribution: {
            navigator: "https://www.jstor.org/stable/26196132?seq=1",
            driver: "https://www.jstor.org/stable/26196132?seq=1"
        },
        communicationStyle: {
            visual: "https://ieeexplore.ieee.org/document/9568912",
            nonvisual: "https://academic.oup.com/joc/article-abstract/52/3/522/4110025?redirectedFrom=fulltext"
        },
        partnerTrying: {
            working: "https://dl.acm.org/doi/abs/10.1145/3498326",
            friendly: "https://dl.acm.org/doi/abs/10.1145/3498326"
        }
    };

    // Add event listeners once the DOM is fully loaded
    document.addEventListener('DOMContentLoaded', function () {
        // Handle info icons
        document.querySelectorAll('.info-icon').forEach(icon => {
            icon.addEventListener('click', function () {
                const popupType = this.id.replace('Info', '');
                console.log(`Info icon clicked: ${popupType}`);
                showPopup(popupType);
            });
        });

        // Handle close button on popup
        const closeButton = document.querySelector('.close-btn');
        if (closeButton) {
            closeButton.addEventListener('click', function () {
                console.log('Popup closed');
                document.getElementById('popup').style.display = 'none';
            });
        }

        // Handle "Why?" link clicks
        const whyLink = document.querySelector('.why-link');
        if (whyLink) {
            whyLink.addEventListener('click', function () {
                const link = this.dataset.link;
                console.log(`Why link clicked, link: ${link}`);
                if (link) {
                    vscode.postMessage({
                        command: 'openLink',
                        link: link
                    });
                }
            });
        }

        // Handle toggle switches
        document.querySelectorAll('.toggle-input').forEach(toggle => {
            toggle.addEventListener('change', function () {
                const type = this.id.replace('Toggle', '');
                const value = this.checked ? 'ON' : 'OFF';
                console.log(`Toggle changed, type: ${type}, value: ${value}`);
                vscode.postMessage({
                    command: 'updateStat',
                    type: type,
                    value: value
                });
            });
        });

        // Handle session ID input and button
        const runTest2Btn = document.getElementById('runTest2Btn');
        if (runTest2Btn) {
            runTest2Btn.addEventListener('click', () => {
                const sessionId = document.getElementById('sessionIdInput').value;
                console.log(`Button clicked, sessionId: ${sessionId}`);
                if (!sessionId) {
                    console.error('Session ID is empty');
                    return;
                }
                vscode.postMessage({
                    command: 'runTest2',
                    sessionId: sessionId
                });
                console.log('Message sent to VSCode extension');
            });
        } else {
            console.error('runTest2Btn element not found');
        }
    });

    // Show the information popup
    function showPopup(type) {
        const popup = document.getElementById('popup');
        const popupText = document.getElementById('popupText');
        const popupIcon = document.querySelector('.popup-icon');
        const whyLink = document.querySelector('.why-link');
        const toggle = document.getElementById(`${type}Toggle`);

        let state;
        switch (type) {
            case 'primaryContribution':
                state = toggle.checked ? 'driver' : 'navigator';
                break;
            case 'communicationStyle':
                state = toggle.checked ? 'visual' : 'nonvisual';
                break;
            case 'partnerTrying':
                state = toggle.checked ? 'working' : 'friendly';
                break;
            default:
                console.error(`Unknown popup type: ${type}`);
                return;
        }

        popupText.textContent = hoverInfo[type][state];
        popupIcon.innerHTML = '💡';
        whyLink.style.color = '#ff0000';
        whyLink.dataset.link = whyLinks[type][state];
        popup.style.display = 'block';
        console.log(`Popup shown for type: ${type}, state: ${state}`);
    }

    // Handle messages from the VSCode extension
    window.addEventListener('message', event => {
        const message = event.data;
        console.log(`Received message from extension: ${JSON.stringify(message)}`);
        switch (message.command) {
            case 'showProgress':
                // Hide the session ID input and show the progress message
                document.querySelector('.session-id-container').classList.add('hidden');
                document.getElementById('progressMessage').classList.remove('hidden');
                break;
            case 'sessionCompleted':
                // Handle session completed if needed
                break;
            default:
                console.error(`Unknown command: ${message.command}`);
        }
    });

    // Update stats display based on received message
    function updateStats(message) {
        document.getElementById('linesOfCode').textContent = message.linesOfCode;
        document.getElementById('interruptionCount').textContent = message.interruptionCount;
        document.getElementById('primaryContributionToggle').checked = message.primaryContribution === 'Driver';
        document.getElementById('communicationStyleToggle').checked = message.communicationStyle === 'Visual';
        document.getElementById('partnerTryingToggle').checked = message.partnerTrying === 'Friendly';
        console.log('Stats updated from extension message');
    }
})();