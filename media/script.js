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

        const endSessionBtn = document.getElementById('endSession');
        if (endSessionBtn) {
            endSessionBtn.addEventListener('click', () => {
                console.log('End Session button clicked');
                // Send a message to the server to end the session
                vscode.postMessage({
                    command: 'endSession'
                });
                console.log('End session message sent to server');
            });
        } else {
            console.error('End Session button not found');
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
            case 'updateData':
                console.log("script.js Line 156");
                if (message.users_data && Array.isArray(message.users_data) && message.users_data.length === 2) {
                    console.log('Received updateData command with data:', message.users_data);
                    const user1 = message.users_data[0] ;// "Your Stats"
                    const user2 = message.users_data[1]; //?.intervals !== null ? message.users_data[1]?.intervals[0] : null; // "Partner Stats"
                    console.log(user1,user2);
                    updateUserStats(user1, user2);
                    document.getElementById('progressMessage').classList.add('hidden');
                    document.getElementById('userStats').classList.remove('hidden');
                    console.log('User stats updated and displayed.');
                } else {
                    console.error('User data is missing or invalid:', message);
                }
                break;
            case 'finalStats':
                if (message.final_data && Array.isArray(message.final_data) && message.final_data.length === 2) {
                    const user1 = message.final_data[0] ;// "Your Stats"
                    const user2 = message.final_data[1]; //?.intervals !== null ? message.users_data[1]?.intervals[0] : null; // "Partner Stats"
                    console.log(user1,user2);
                    updateFinalStats(user1, user2);
                    document.getElementById('progressMessage').classList.add('hidden');
                    document.getElementById('userStats').classList.add('hidden');
                    document.getElementById('finalStats').classList.remove('hidden');
                    console.log('User stats updated and displayed.');
                } else {
                    console.error('User data is missing or invalid:', message);
                }
                break;
            case 'sessionCompleted':
                // Only handle the session as completed when all data has been processed
            document.getElementById('progressMessage').classList.add('hidden');
            const statsContainer = document.getElementById('userStats');
            statsContainer.classList.remove('hidden');
            // Display final stats or additional completion actions
            break;
            default:
                console.error(`Unknown command: ${message.command}`);
        }
    });
    function updateUserStats(user1, user2) {
        console.log('Updating user stats with:', user1, user2);
        // Update stats for User 1
        document.getElementById('user1PrimaryContribution').textContent = user1.role;
        driver_u1 = "You are actively writing most of the code.";
        nav_u1 = "You are guiding the session. Focus on the direction and strategy for code writing.";
        document.getElementById('user1PrimaryContributionTip').textContent = user1.role === "Driver" ? driver_u1 : nav_u1;
        document.getElementById('user1CommunicationStyle').textContent = user1.communication_style;
        verbal_u1 = "You focused on clearly conveying your thoughts. Keep it up !";
        nonVerbal_u1= "Remember to clearly communicate your thought process with your partner.";
        document.getElementById('user1CommunicationStyleTip').textContent  = user1.communication_style === "Verbal" ? verbal_u1 : nonVerbal_u1;
        user1SelfEff = user1.self_efficacy[0] > user1.self_efficacy[1] ? "High" : "Low";
        document.getElementById('user1SelfEfficacy').textContent = user1SelfEff;
        sfHigh_u1 = "You are being proactive and confident. Keep up with the high energy.";
        sfLow_u1 = "While you may have benefited from your partner's input, it would be helpful to explore ways to build your own confidence and decision-making skills.";
        document.getElementById('user1SelfEfficacyTip').textContent = user1SelfEff === "High" ? sfHigh_u1 : sfLow_u1;
        document.getElementById('user1Interruptions').textContent = user1.interruptions;
        document.getElementById('user1InterruptionsTip').textContent = "You interrupted your partner " + user1.interruptions + " times in last 5 minutes.";
        document.getElementById('user1Leadership').textContent = user1.leadership;
        auth_u1 = "You are confidently directing the session ensuring progress, however consider involving your partner in decision making.";
        dem_u1 = "You are displaying a collaborative leadership style by involving your partner in decision-making. Keep it up!";
        document.getElementById('user1LeadershipTip').textContent = user1.leadership === "Democratic" ? dem_u1 : auth_u1;
        rapport_u1a = "Keep up with building friendly connection with your partner but make sure you are focused on the task.";
        rapport_u1b = "Continue focusing on the task,but remember to be friendly with your partner to build connection.";
        document.getElementById('user1RapportTip').textContent = user1.rapport_score > 0.5 ? rapport_u1a : rapport_u1b;
    
        // Update stats for User 2
        document.getElementById('user2PrimaryContribution').textContent = user2.role;
        driver_u2 = "Your partner is actively writing most of the code";
        nav_u2= "Your partner is guiding the session effectively.";
        document.getElementById('user2PrimaryContributionTip').textContent = user2.role === "Driver" ? driver_u2 : nav_u2;

        document.getElementById('user2CommunicationStyle').textContent = user2.communication_style;
        verbal_u2= "Your partner is primarily communicating their thoughts verbally to ensure clarity.";
        nonVerbal_u2= "Your partner is primarily communicating their thoughts through facial expressions.";
        document.getElementById('user2CommunicationStyleTip').textContent = user2.communication_style === "Verbal" ?  verbal_u2 : nonVerbal_u2;

        user2SelfEff = user2.self_efficacy[0] > user2.self_efficacy[1] ? "High" : "Low";
        document.getElementById('user2SelfEfficacy').textContent = user2SelfEff;
        sfHigh_u2 = "Your partner is proactive and has a positive mindset.";
        sfLow_u2 = "Your partner is hesitant and is relying more on your guidance and validation.";
        document.getElementById('user2SelfEfficacyTip').textContent = user2SelfEff === "High" ? sfHigh_u2 : sfLow_u2;

        rapport_u2a = "Your partner is making conversation with you and attempting to be friendly.";
        rapport_u2b ="Your partner seems more invested in task than casual conversation.";
        document.getElementById('user2RapportTip').textContent = user2.rapport_score > 0.5 ? rapport_u2a : rapport_u2b;
        //Update session stats
        document.getElementById('sessionLOC').textContent = user1.loc + user2.loc;
    }

    function updateFinalStats(user1,user2){
        console.log('updating final stats');
        document.getElementById('user1FinalRole').textContent = user1.role;
        document.getElementById('user1FinalComm').textContent = user1.communication_style;
        document.getElementById('user1FinalEfficacy').textContent = user1.self_efficacy[0] > user1.self_efficacy[1] ? "High" : "Low";
        document.getElementById('user1FinalInterr').textContent = user1.interruptions;
        document.getElementById('user1FinalLeadership').textContent = user1.leadership;
        rapport_u1a = "Keep up with building friendly connection with your partner but make sure you are focused on the task.";
        rapport_u1b = "Continue focusing on the task,but remember to be friendly with your partner to build connection.";
        document.getElementById('user1FinalRapport').textContent = user1.rapport_score > 0.5 ? rapport_u1a : rapport_u1b;
    
        // Update stats for User 2
        document.getElementById('user2FinalRole').textContent = user2.role;
        document.getElementById('user2FinalComm').textContent = user2.communication_style;
        document.getElementById('user2FinalEfficacy').textContent = user2.self_efficacy[0] > user2.self_efficacy[1] ? "High" : "Low";
        rapport_u2a = "Your partner is making conversation with you and attempting to be friendly.";
        rapport_u2b ="Your partner seems more invested in task than casual conversation";
        document.getElementById('user2FinalRapport').textContent = user2.rapport_score > 0.5 ? rapport_u2a : rapport_u2b;
        //Update session stats
        document.getElementById('sessionFinalLOC').textContent = user1.loc + user2.loc;
    }

})();
