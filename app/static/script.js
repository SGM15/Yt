document.addEventListener('DOMContentLoaded', () => {
    // --- Navigation Logic ---
    const views = {
        'nav-dashboard': 'view-dashboard',
        'nav-buddy': 'view-chat',
        'nav-all-teams': 'view-teams',
        'nav-contact': 'view-contact'
    };

    function switchView(viewId) {
        // Hide all views
        document.querySelectorAll('.view-section').forEach(el => el.classList.remove('active'));
        // Show selected view
        document.getElementById(viewId).classList.add('active');
        
        // Update active nav item
        document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
        // Find the nav item that maps to this view
        for (const [navId, vId] of Object.entries(views)) {
            if (vId === viewId) {
                const navEl = document.getElementById(navId);
                if (navEl) navEl.classList.add('active');
                break;
            }
        }
    }

    // Attach click listeners to main nav items
    for (const [navId, viewId] of Object.entries(views)) {
        const navEl = document.getElementById(navId);
        if (navEl) {
            navEl.addEventListener('click', () => switchView(viewId));
        }
    }

    // --- Chat Logic ---
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatContainer = document.getElementById('chat-container');
    const userId = 'user_' + Math.random().toString(36).substr(2, 9);

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        userInput.value = '';
        const loadingId = addLoadingIndicator();

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: message, user_id: userId }),
            });

            if (!response.ok) throw new Error('Network response was not ok');
            const data = await response.json();
            
            removeMessage(loadingId);
            addMessage(data.response, 'bot');
            fetchTeams(); // Refresh teams after chat
        } catch (error) {
            console.error('Error:', error);
            removeMessage(loadingId);
            addMessage('Sorry, something went wrong.', 'bot');
        }
    });

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', `${sender}-message`);
        
        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('avatar');
        avatarDiv.textContent = sender === 'bot' ? 'T' : 'U';
        
        const bodyDiv = document.createElement('div');
        bodyDiv.classList.add('message-body');
        
        const infoDiv = document.createElement('div');
        infoDiv.classList.add('message-info');
        
        const nameSpan = document.createElement('span');
        nameSpan.classList.add('sender-name');
        nameSpan.textContent = sender === 'bot' ? 'TrackUp Bot' : 'You';
        
        const timeSpan = document.createElement('span');
        timeSpan.classList.add('timestamp');
        timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        infoDiv.appendChild(nameSpan);
        infoDiv.appendChild(timeSpan);
        
        const contentDiv = document.createElement('div');
        contentDiv.classList.add('message-content');
        contentDiv.textContent = text;
        
        bodyDiv.appendChild(infoDiv);
        bodyDiv.appendChild(contentDiv);
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(bodyDiv);
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function addLoadingIndicator() {
        const id = 'loading-' + Date.now();
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', 'bot-message');
        messageDiv.id = id;
        
        const avatarDiv = document.createElement('div');
        avatarDiv.classList.add('avatar');
        avatarDiv.textContent = 'T';
        
        const bodyDiv = document.createElement('div');
        bodyDiv.classList.add('message-body');
        
        const infoDiv = document.createElement('div');
        infoDiv.classList.add('message-info');
        
        const nameSpan = document.createElement('span');
        nameSpan.classList.add('sender-name');
        nameSpan.textContent = 'TrackUp Bot';
        
        infoDiv.appendChild(nameSpan);
        
        const indicatorDiv = document.createElement('div');
        indicatorDiv.classList.add('typing-indicator');
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('div');
            dot.classList.add('dot');
            indicatorDiv.appendChild(dot);
        }
        
        bodyDiv.appendChild(infoDiv);
        bodyDiv.appendChild(indicatorDiv);
        
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(bodyDiv);
        
        chatContainer.appendChild(messageDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        
        return id;
    }

    function removeMessage(id) {
        const element = document.getElementById(id);
        if (element) element.remove();
    }

    // --- Modal Logic ---
    const modal = document.getElementById('member-modal');
    const closeModal = document.querySelector('.close-modal');
    const modalName = document.getElementById('modal-member-name');
    const modalCompleted = document.getElementById('modal-completed');
    const modalTotal = document.getElementById('modal-total');
    const modalTasksList = document.getElementById('modal-tasks-list');
    const modalChatBtn = document.getElementById('modal-chat-btn');

    if (closeModal) {
        closeModal.addEventListener('click', () => {
            modal.classList.remove('active');
        });
    }

    window.onclick = (event) => {
        if (event.target == modal) {
            modal.classList.remove('active');
        }
    };

    async function openMemberModal(memberName) {
        modalName.textContent = memberName;
        modalCompleted.textContent = '-';
        modalTotal.textContent = '-';
        modalTasksList.innerHTML = '<p style="padding:10px;">Loading...</p>';
        modal.classList.add('active');

        // Setup Chat Button
        modalChatBtn.onclick = () => {
            modal.classList.remove('active');
            startChatWith(memberName);
        };

        try {
            const response = await fetch(`/api/member/${encodeURIComponent(memberName)}`);
            if (response.ok) {
                const data = await response.json();
                modalCompleted.textContent = data.completed_tasks;
                modalTotal.textContent = data.total_tasks;
                
                modalTasksList.innerHTML = '';
                if (data.tasks.length === 0) {
                    modalTasksList.innerHTML = '<p style="padding:10px; color:#888;">No tasks assigned.</p>';
                } else {
                    data.tasks.forEach(task => {
                        const div = document.createElement('div');
                        div.classList.add('task-item');
                        div.innerHTML = `
                            <span>${task.title}</span>
                            <div style="display:flex; align-items:center; gap:10px;">
                                <span class="task-status ${task.status}">${task.status}</span>
                                <button class="delete-task-btn" style="background:none; border:none; color:#dc3545; cursor:pointer;">&times;</button>
                            </div>
                        `;
                        div.querySelector('.delete-task-btn').onclick = async () => {
                            if(confirm('Delete this task?')) {
                                await fetch(`/api/tasks/${task.id}`, { method: 'DELETE' });
                                openMemberModal(memberName); // Refresh modal
                            }
                        };
                        modalTasksList.appendChild(div);
                    });
                }
            }
        } catch (error) {
            console.error('Error fetching member details:', error);
            modalTasksList.innerHTML = '<p style="padding:10px; color:red;">Error loading details.</p>';
        }
    }

    // --- File Upload Logic ---
    const attachBtn = document.getElementById('attach-btn');
    const fileInput = document.getElementById('file-upload');

    attachBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', () => {
        if (fileInput.files.length > 0) {
            const fileName = fileInput.files[0].name;
            userInput.value = `[Attached: ${fileName}] ` + userInput.value;
            userInput.focus();
        }
    });

    // --- Teams Logic ---
    async function fetchTeams() {
        try {
            const response = await fetch('/api/teams');
            if (response.ok) {
                const teams = await response.json();
                renderTeams(teams);
            }
        } catch (error) {
            console.error('Error fetching teams:', error);
        }
    }

    function renderTeams(teams) {
        const navList = document.getElementById('teams-nav-list');
        const detailContainer = document.getElementById('teams-detail-container');
        
        navList.innerHTML = '';
        detailContainer.innerHTML = '';

        if (Object.keys(teams).length === 0) {
            navList.innerHTML = '<div style="padding: 10px 15px; color: #888;">No teams</div>';
            detailContainer.innerHTML = '<p>No teams found. Ask TrackUp Buddy to create one!</p>';
            return;
        }

        for (const [teamName, members] of Object.entries(teams)) {
            // 1. Add to Sidebar
            const navItem = document.createElement('div');
            navItem.classList.add('nav-item');
            navItem.innerHTML = `<span>#</span> ${teamName}`;
            navItem.addEventListener('click', () => {
                switchView('view-teams');
                const card = document.getElementById(`team-card-${teamName}`);
                if (card) card.scrollIntoView({ behavior: 'smooth' });
            });
            navList.appendChild(navItem);

            // 2. Add to Detail View
            const teamCard = document.createElement('div');
            teamCard.classList.add('team-detail-card');
            teamCard.id = `team-card-${teamName}`;
            
            const cardHeader = document.createElement('div');
            cardHeader.style.display = 'flex';
            cardHeader.style.justifyContent = 'space-between';
            cardHeader.style.alignItems = 'center';
            cardHeader.style.borderBottom = '1px solid #eee';
            cardHeader.style.paddingBottom = '10px';
            
            const title = document.createElement('h3');
            title.textContent = teamName;
            title.style.margin = '0';
            
            const deleteTeamBtn = document.createElement('button');
            deleteTeamBtn.textContent = 'Delete Team';
            deleteTeamBtn.style.background = '#dc3545';
            deleteTeamBtn.style.color = 'white';
            deleteTeamBtn.style.border = 'none';
            deleteTeamBtn.style.padding = '5px 10px';
            deleteTeamBtn.style.borderRadius = '4px';
            deleteTeamBtn.style.cursor = 'pointer';
            deleteTeamBtn.style.fontSize = '0.8em';
            deleteTeamBtn.onclick = async () => {
                if(confirm(`Are you sure you want to delete team ${teamName}?`)) {
                    await fetch(`/api/teams/${teamName}`, { method: 'DELETE' });
                    fetchTeams();
                }
            };

            cardHeader.appendChild(title);
            cardHeader.appendChild(deleteTeamBtn);
            
            const membersList = document.createElement('div');
            if (members.length === 0) {
                membersList.innerHTML = '<p style="color: #888; font-style: italic;">No members yet</p>';
            } else {
                members.forEach(member => {
                    const row = document.createElement('div');
                    row.classList.add('team-member-row');
                    row.innerHTML = `
                        <span class="member-name-link" style="cursor:pointer; color:#3F0E40; font-weight:500;">${member}</span>
                        <div style="display:flex; gap:10px;">
                            <button class="chat-btn-small" onclick="startChatWith('${member}')">Message</button>
                            <button class="delete-btn-small" style="background:none; border:none; color:#dc3545; cursor:pointer;">&times;</button>
                        </div>
                    `;
                    row.querySelector('.member-name-link').addEventListener('click', () => openMemberModal(member));
                    row.querySelector('.delete-btn-small').addEventListener('click', async () => {
                        if(confirm(`Remove ${member} from ${teamName}?`)) {
                            await fetch(`/api/teams/${teamName}/members/${member}`, { method: 'DELETE' });
                            fetchTeams();
                        }
                    });
                    membersList.appendChild(row);
                });
            }

            teamCard.appendChild(cardHeader);
            teamCard.appendChild(membersList);
            detailContainer.appendChild(teamCard);
        }
    }

    // Helper to start chat from team view
    window.startChatWith = function(memberName) {
        switchView('view-chat');
        userInput.value = `Message for ${memberName}: `;
        userInput.focus();
    };

    // Initial Load
    fetchTeams();
});
