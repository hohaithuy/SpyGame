const MATCH_CACHE_KEY = "spygame_active_match";
const MATCH_CACHE_VERSION = 1;
const MIN_WORDS_PER_CLUSTER = 4;
const VIETNAMESE_LETTERS_PATTERN = /^[A-Za-zÀ-ỹĐđ]+ [A-Za-zÀ-ỹĐđ]+$/u;

// Application State
const state = {
    wordDatabase: null,
    databaseStatus: "loading",
    roster: [],             // Persistent score table across rounds
    nextPlayerId: 1,
    players: [],            // Players participating in the current round
    revealIndex: 0,
    playedClusterIds: new Set(),
    currentCategory: "",
    currentClusterTheme: "",
    civilianWord: "",
    spyWord: "",
    speakingOrder: [],
    roundOutcome: "",
    roundResolved: false,
    spyGuessMode: null,
    outcomeDialog: null
};

let pendingCachedMatch = null;

// Sound synthesizer using Web Audio API (for premium haptic feedback)
const soundEffects = {
    ctx: null,
    init() {
        if (!this.ctx) {
            this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        }
    },
    playClick() {
        this.init();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        
        osc.frequency.setValueAtTime(800, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(100, this.ctx.currentTime + 0.1);
        gain.gain.setValueAtTime(0.08, this.ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0.01, this.ctx.currentTime + 0.1);
        
        osc.start();
        osc.stop(this.ctx.currentTime + 0.1);
    },
    playReveal() {
        this.init();
        const osc = this.ctx.createOscillator();
        const gain = this.ctx.createGain();
        osc.connect(gain);
        gain.connect(this.ctx.destination);
        
        osc.type = "triangle";
        osc.frequency.setValueAtTime(300, this.ctx.currentTime);
        osc.frequency.exponentialRampToValueAtTime(600, this.ctx.currentTime + 0.2);
        gain.gain.setValueAtTime(0.12, this.ctx.currentTime);
        gain.gain.linearRampToValueAtTime(0.01, this.ctx.currentTime + 0.25);
        
        osc.start();
        osc.stop(this.ctx.currentTime + 0.25);
    }
};

// UI Toggles & Element selections
const screens = {
    setup: document.getElementById("screen-setup"),
    reveal: document.getElementById("screen-reveal"),
    play: document.getElementById("screen-play"),
    summary: document.getElementById("screen-summary"),
    
    show(screenElement) {
        Object.values(screens).forEach(scr => {
            if (scr && typeof scr === "object" && "classList" in scr) {
                scr.classList.remove("active");
            }
        });
        screenElement.classList.add("active");

        const canEditNextRound = screenElement === screens.play || screenElement === screens.summary;
        btnOpenSettings.hidden = !canEditNextRound;
        if (!canEditNextRound) {
            closeSettings();
        }
    }
};

// DOM Elements
const textareaNames = document.getElementById("names-input");
const countBadge = document.getElementById("names-count");
const warningAlert = document.getElementById("warning-alert");
const warningText = document.getElementById("warning-text");

const blankChance = document.getElementById("blank-chance");

const btnStart = document.getElementById("btn-start");
const btnOpenSettings = document.getElementById("btn-open-settings");
const settingsModal = document.getElementById("settings-modal");
const btnCloseSettings = document.getElementById("btn-close-settings");
const btnSettingsDone = document.getElementById("btn-settings-done");
const settingsBlankChance = document.getElementById("settings-blank-chance");
const settingsActiveCount = document.getElementById("settings-active-count");
const settingsPlayerList = document.getElementById("settings-player-list");
const settingsAddPlayerForm = document.getElementById("settings-add-player-form");
const settingsNewPlayer = document.getElementById("settings-new-player");
const settingsMessage = document.getElementById("settings-message");
const resumeModal = document.getElementById("resume-modal");
const btnResumeMatch = document.getElementById("btn-resume-match");
const btnNewMatch = document.getElementById("btn-new-match");

// Reveal Phase Elements
const revealName = document.getElementById("reveal-player-name");
const revealPrompt = document.getElementById("reveal-prompt");
const cardContainer = document.getElementById("card-container");
const cardBack = document.getElementById("card-back");
const cardRoleBadge = document.getElementById("card-role-badge");
const cardWordTitle = document.getElementById("card-word-title");
const cardWordVal = document.getElementById("card-word-val");
const cardBottomInstruction = document.getElementById("card-bottom-instruction");
const btnRevealAction = document.getElementById("btn-reveal-action");

// Play Board Elements
const speakingList = document.getElementById("speaking-list");
const outcomeModal = document.getElementById("outcome-modal");
const outcomeTitle = document.getElementById("outcome-title");
const outcomeMessage = document.getElementById("outcome-message");
const spyClaimActions = document.getElementById("spy-claim-actions");
const spyGuessActions = document.getElementById("spy-guess-actions");
const btnSpyClaim = document.getElementById("btn-spy-claim");
const btnConfirmSpyClaim = document.getElementById("btn-confirm-spy-claim");
const btnCancelSpyClaim = document.getElementById("btn-cancel-spy-claim");
const btnSpyCorrect = document.getElementById("btn-spy-correct");
const btnSpyWrong = document.getElementById("btn-spy-wrong");
const btnShowSummary = document.getElementById("btn-show-summary");

// Summary Elements
const summaryCategoryTag = document.getElementById("summary-category");
const summaryCivilianWord = document.getElementById("summary-civilian-word");
const summarySpyWord = document.getElementById("summary-spy-word");
const summaryRoundOutcome = document.getElementById("summary-round-outcome");
const scoreboardList = document.getElementById("scoreboard-list");
const summaryList = document.getElementById("summary-list");
const btnNextRound = document.getElementById("btn-next-round");

// Initialization & Database loading
function isValidWordPhrase(value) {
    if (typeof value !== "string") return false;

    const normalized = value.trim().replace(/\s+/g, " ");
    const words = normalized.split(" ");
    return words.length === 2
        && [...normalized].every(char => char === " " || /^\p{L}$/u.test(char))
        && VIETNAMESE_LETTERS_PATTERN.test(normalized);
}

function isValidWordDatabase(database) {
    return Array.isArray(database?.categories)
        && database.categories.length > 0
        && database.categories.every(category =>
            Array.isArray(category.clusters)
            && category.clusters.length > 0
            && category.clusters.every(cluster => {
                if (!Array.isArray(cluster.words) || cluster.words.length < MIN_WORDS_PER_CLUSTER) {
                    return false;
                }

                const normalizedWords = cluster.words.map(word =>
                    typeof word === "string" ? word.trim().toLocaleLowerCase("vi") : ""
                );
                return cluster.words.every(isValidWordPhrase)
                    && new Set(normalizedWords).size === normalizedWords.length;
            })
        );
}

async function loadDatabase() {
    try {
        const response = await fetch("./data/words.json");
        if (!response.ok) {
            throw new Error("Could not fetch words.json");
        }

        const database = await response.json();
        if (!isValidWordDatabase(database)) {
            throw new Error("words.json contains invalid word clusters");
        }

        state.wordDatabase = database;
        state.databaseStatus = "ready";
        console.log("SpyGame: Loaded word database successfully.");
    } catch (error) {
        state.wordDatabase = null;
        state.databaseStatus = "error";
        console.error("SpyGame: Could not load a valid data/words.json file.", error);
    }
    validateConfig();
}

// Extract player names from textarea
function getPlayerNames() {
    return textareaNames.value
        .split("\n")
        .map(name => name.trim())
        .filter(name => name.length > 0);
}

function resizeNamesInput() {
    textareaNames.style.height = "auto";
    textareaNames.style.height = `${textareaNames.scrollHeight}px`;
}

// Auto-updates player names badge
function updatePlayerCount() {
    resizeNamesInput();
    const names = getPlayerNames();
    countBadge.textContent = `${names.length} người`;
    validateConfig();
}

// Configuration validation
function validateConfig() {
    const names = getPlayerNames();
    const n = names.length;

    if (state.databaseStatus === "loading") {
        btnStart.disabled = true;
        return false;
    }

    if (state.databaseStatus === "error") {
        showWarning("Không thể tải dữ liệu từ. Hãy tạo hoặc kiểm tra lại data/words.json rồi tải lại trang.");
        btnStart.disabled = true;
        return false;
    }
    
    if (n < 3) {
        showWarning("Trò chơi cần ít nhất 3 người chơi để bắt đầu.");
        btnStart.disabled = true;
        return false;
    }
    
    hideWarning();
    btnStart.disabled = false;
    return true;
}

function showWarning(msg) {
    warningText.textContent = msg;
    warningAlert.style.display = "flex";
}

function hideWarning() {
    warningAlert.style.display = "none";
}

// Randomly Select Word Pair
function selectWordPair() {
    const categories = state.wordDatabase.categories;
    
    // Build a flat list of available clusters across all categories
    let availableClusters = [];
    categories.forEach(cat => {
        cat.clusters.forEach((cluster, idx) => {
            const clusterId = `${cat.id}_${idx}`;
            if (!state.playedClusterIds.has(clusterId)) {
                availableClusters.push({
                    id: clusterId,
                    categoryName: cat.name,
                    icon: cat.icon || "🎮",
                    theme: cluster.theme,
                    words: cluster.words
                });
            }
        });
    });
    
    // Reset played list if all have been played
    if (availableClusters.length === 0) {
        console.log("🔄 SpyGame: All word pairs have been played! Resetting history.");
        state.playedClusterIds.clear();
        return selectWordPair(); // Recurse
    }
    
    // Choose a random cluster
    const chosen = availableClusters[Math.floor(Math.random() * availableClusters.length)];
    state.playedClusterIds.add(chosen.id);
    localStorage.setItem("spygame_played_ids", JSON.stringify(Array.from(state.playedClusterIds)));
    
    state.currentCategory = `${chosen.icon} ${chosen.categoryName}`;
    state.currentClusterTheme = chosen.theme;
    
    // Shuffle and pick 2 words from cluster
    const words = [...chosen.words];
    shuffleArray(words);
    
    state.civilianWord = words[0];
    state.spyWord = words[1];
}

// Helper: Shuffle Array in-place
function shuffleArray(array) {
    for (let i = array.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [array[i], array[j]] = [array[j], array[i]];
    }
}

function createRosterPlayer(name) {
    return {
        id: state.nextPlayerId++,
        name,
        score: 0,
        active: true
    };
}

function getActiveRoster() {
    return state.roster.filter(player => player.active);
}

function getCurrentGamePhase() {
    if (screens.reveal.classList.contains("active")) return "reveal";
    if (screens.play.classList.contains("active")) return "play";
    if (screens.summary.classList.contains("active")) return "summary";
    return null;
}

function saveCachedMatch(phase = getCurrentGamePhase()) {
    if (!phase || state.roster.length === 0) return;

    const snapshot = {
        version: MATCH_CACHE_VERSION,
        phase,
        blankChance: blankChance.value,
        roster: state.roster,
        nextPlayerId: state.nextPlayerId,
        players: state.players,
        revealIndex: state.revealIndex,
        playedClusterIds: Array.from(state.playedClusterIds),
        currentCategory: state.currentCategory,
        currentClusterTheme: state.currentClusterTheme,
        civilianWord: state.civilianWord,
        spyWord: state.spyWord,
        speakingOrder: state.speakingOrder,
        roundOutcome: state.roundOutcome,
        roundResolved: state.roundResolved,
        spyGuessMode: state.spyGuessMode,
        outcomeDialog: state.outcomeDialog
    };

    localStorage.setItem(MATCH_CACHE_KEY, JSON.stringify(snapshot));
}

function loadCachedMatch() {
    const savedMatch = localStorage.getItem(MATCH_CACHE_KEY);
    if (!savedMatch) return null;

    try {
        const snapshot = JSON.parse(savedMatch);
        const validPhase = ["reveal", "play", "summary"].includes(snapshot.phase);
        if (
            snapshot.version !== MATCH_CACHE_VERSION ||
            !validPhase ||
            !Array.isArray(snapshot.roster) ||
            !Array.isArray(snapshot.players)
        ) {
            throw new Error("Invalid saved match");
        }
        return snapshot;
    } catch (error) {
        localStorage.removeItem(MATCH_CACHE_KEY);
        return null;
    }
}

function clearCachedMatch() {
    localStorage.removeItem(MATCH_CACHE_KEY);
}

function saveActiveNames() {
    const activeNames = getActiveRoster().map(player => player.name).join("\n");
    localStorage.setItem("spygame_names", activeNames);
}

// Role Assignor Engine
function assignRolesAndWords() {
    const participants = getActiveRoster();
    const total = participants.length;
    const hasBlank = Math.random() * 100 < Number(blankChance.value);
    
    selectWordPair();
    
    // Build role pool
    const roles = ["spy"];
    if (hasBlank) roles.push("blank");
    while (roles.length < total) roles.push("civilian");
    
    shuffleArray(roles);
    
    // Assign to players
    state.players = participants.map((participant, idx) => {
        const role = roles[idx];
        let word = "";
        if (role === "civilian") {
            word = state.civilianWord;
        } else if (role === "spy") {
            word = state.spyWord;
        } else if (role === "blank") {
            word = "???"; // Blank players don't know the word
        }
        return {
            id: participant.id,
            name: participant.name,
            role,
            word
        };
    });
}

function determineSpeakingOrder() {
    state.speakingOrder = state.players.map((_, idx) => idx);
    shuffleArray(state.speakingOrder);
}

// Start Game Event
function startGame() {
    if (!validateConfig()) return;
    
    soundEffects.playReveal();
    
    // Save names to local storage for persistence
    const names = getPlayerNames();
    localStorage.setItem("spygame_names", names.join("\n"));
    state.nextPlayerId = 1;
    state.roster = names.map(name => createRosterPlayer(name));
    
    assignRolesAndWords();
    determineSpeakingOrder();
    
    // Setup reveal phase
    state.revealIndex = 0;
    setupNextPlayerReveal();
    screens.show(screens.reveal);
    saveCachedMatch("reveal");
}

// Card Reveal flow controllers
function setupNextPlayerReveal() {
    const p = state.players[state.revealIndex];
    revealName.textContent = p.name;
    revealPrompt.textContent = "Nhấp vào thẻ bên dưới để xem vai trò bí mật";
    
    // Reset Card Visual State
    cardContainer.classList.remove("flipped");
    cardBack.className = "card-face card-back"; // Clear roles classes
    
    // Assign backend card contents
    if (p.role === "civilian") {
        cardBack.classList.add("role-civilian");
        cardRoleBadge.textContent = "Dân Thường 🧑‍🌾";
        cardWordTitle.textContent = "Từ bí mật của bạn";
        cardWordVal.textContent = p.word;
        cardBottomInstruction.textContent = "Tìm ra Gián Điệp, nhưng cẩn thận: bỏ phiếu loại Dân Trắng sẽ giúp họ chiến thắng!";
    } else if (p.role === "spy") {
        cardBack.classList.add("role-spy");
        cardRoleBadge.textContent = "Gián Điệp 🕵️";
        cardWordTitle.textContent = "Từ bí mật của bạn";
        cardWordVal.textContent = p.word;
        cardBottomInstruction.textContent = "Hòa nhập và tránh bị loại. Đừng vô tình trao chiến thắng cho Dân Trắng!";
    } else if (p.role === "blank") {
        cardBack.classList.add("role-blank");
        cardRoleBadge.textContent = "Dân Trắng 🤍";
        cardWordTitle.textContent = "Mục tiêu của bạn";
        cardWordVal.textContent = "Bị Loại";
        cardBottomInstruction.textContent = "Bạn không có từ. Hãy khiến mọi người bỏ phiếu loại bạn. Nếu bị loại, bạn chiến thắng!";
    }
    
    btnRevealAction.textContent = "Xem vai trò bí mật";
    btnRevealAction.className = "btn btn-primary";
}

function handleCardRevealToggle() {
    const isFlipped = cardContainer.classList.contains("flipped");
    
    if (!isFlipped) {
        // Reveal Card
        soundEffects.playReveal();
        cardContainer.classList.add("flipped");
        revealPrompt.textContent = "Hãy ghi nhớ vai trò và nhấp nút màu cam để xác nhận";
        btnRevealAction.textContent = "Tôi đã nhớ rõ vai trò! (Truyền máy)";
        btnRevealAction.className = "btn btn-accent-gold";
    } else {
        // Memorized & transition to next player or play screen
        soundEffects.playClick();
        cardContainer.classList.remove("flipped");
        
        // Timeout to allow card to flip back before changing text
        setTimeout(() => {
            state.revealIndex++;
            if (state.revealIndex < state.players.length) {
                setupNextPlayerReveal();
                saveCachedMatch("reveal");
            } else {
                initPlayBoard();
                screens.show(screens.play);
                saveCachedMatch("play");
            }
        }, 300);
    }
}

// Gameplay Board speaking order and voting setup
function initPlayBoard() {
    state.roundResolved = false;
    state.roundOutcome = "";
    state.spyGuessMode = null;
    state.outcomeDialog = null;
    outcomeModal.classList.remove("visible");
    outcomeModal.setAttribute("aria-hidden", "true");
    renderPlayBoard();
}

function renderPlayBoard() {
    speakingList.innerHTML = "";

    state.speakingOrder.forEach((pIdx, orderNum) => {
        const player = state.players[pIdx];
        const row = document.createElement("div");
        row.className = "speaker-row";
        if (orderNum === 0) row.classList.add("first-speaker");

        const position = document.createElement("div");
        position.className = "speaker-num";
        position.textContent = orderNum + 1;

        const name = document.createElement("div");
        name.className = "speaker-name";
        name.textContent = player.name;

        const voteButton = document.createElement("button");
        voteButton.className = "vote-btn";
        voteButton.type = "button";
        voteButton.textContent = "Vote";
        voteButton.setAttribute("aria-label", `Bỏ phiếu ${player.name}`);
        voteButton.addEventListener("click", () => handleVote(pIdx));
        voteButton.disabled = state.roundResolved;

        row.append(position, name, voteButton);
        speakingList.appendChild(row);
    });

    btnSpyClaim.disabled = state.roundResolved;
}

function addScore(playerId, points) {
    const player = state.roster.find(entry => entry.id === playerId);
    if (player) {
        player.score += points;
    }
}

function showOutcomeModal(title, message, needsSpyGuess = false, needsSpyConfirmation = false) {
    state.outcomeDialog = { title, message, needsSpyGuess, needsSpyConfirmation };
    outcomeTitle.textContent = title;
    outcomeMessage.textContent = message;
    spyClaimActions.style.display = needsSpyConfirmation ? "grid" : "none";
    spyGuessActions.style.display = needsSpyGuess ? "grid" : "none";
    btnShowSummary.style.display = needsSpyGuess || needsSpyConfirmation ? "none" : "flex";
    outcomeModal.classList.add("visible");
    outcomeModal.setAttribute("aria-hidden", "false");
}

function promptVoluntarySpyGuess() {
    if (state.roundResolved) return;
    soundEffects.playClick();
    showOutcomeModal(
        "Spy muốn đoán từ?",
        "Chỉ xác nhận nếu bạn là Gián Điệp. Đoán từ sẽ kết thúc vòng này.",
        false,
        true
    );
}

function cancelVoluntarySpyGuess() {
    state.outcomeDialog = null;
    outcomeModal.classList.remove("visible");
    outcomeModal.setAttribute("aria-hidden", "true");
}

function beginVoluntarySpyGuess() {
    if (state.roundResolved) return;

    state.roundResolved = true;
    state.spyGuessMode = "voluntary";
    speakingList.querySelectorAll(".vote-btn").forEach(button => {
        button.disabled = true;
    });
    btnSpyClaim.disabled = true;

    const spy = state.players.find(player => player.role === "spy");
    showOutcomeModal(
        "Spy chủ động đoán từ",
        `${spy.name} là Gián Điệp. Kết quả đoán từ của Dân Thường là gì?`,
        true
    );
    saveCachedMatch("play");
}

function handleVote(playerIndex) {
    if (state.roundResolved) return;
    state.roundResolved = true;
    speakingList.querySelectorAll(".vote-btn").forEach(button => {
        button.disabled = true;
    });
    btnSpyClaim.disabled = true;

    const votedPlayer = state.players[playerIndex];
    const spy = state.players.find(player => player.role === "spy");

    if (votedPlayer.role === "blank") {
        addScore(votedPlayer.id, 2);
        state.roundOutcome = `${votedPlayer.name} là Dân Trắng và thắng vòng này (+2 điểm).`;
        showOutcomeModal("Dân Trắng chiến thắng!", state.roundOutcome);
    } else if (votedPlayer.role === "spy") {
        state.spyGuessMode = "caught";
        showOutcomeModal(
            "Đã bắt được Gián Điệp!",
            `${votedPlayer.name} được quyền đoán từ của Dân Thường. Kết quả là gì?`,
            true
        );
    } else {
        addScore(spy.id, 2);
        state.roundOutcome = `Vote nhầm ${votedPlayer.name}. Gián Điệp sống sót và nhận +2 điểm.`;
        showOutcomeModal("Gián Điệp thoát thân!", state.roundOutcome);
    }
    saveCachedMatch("play");
}

function resolveSpyGuess(isCorrect) {
    const spy = state.players.find(player => player.role === "spy");

    if (isCorrect) {
        const points = state.spyGuessMode === "voluntary" ? 2 : 1;
        addScore(spy.id, points);
        const context = state.spyGuessMode === "voluntary" ? "chủ động đoán đúng" : "bị bắt nhưng đoán đúng";
        state.roundOutcome = `${spy.name} ${context} từ và nhận +${points} điểm.`;
        showOutcomeModal("Gián Điệp chiến thắng!", state.roundOutcome);
        saveCachedMatch("play");
        return;
    }

    state.players.forEach(player => {
        if (player.role === "civilian") {
            addScore(player.id, 1);
        }
    });
    const context = state.spyGuessMode === "voluntary" ? "chủ động đoán sai" : "đoán sai";
    state.roundOutcome = `Gián Điệp ${context}. Mỗi Dân Thường nhận +1 điểm.`;
    showOutcomeModal("Dân Thường chiến thắng!", state.roundOutcome);
    saveCachedMatch("play");
}

function renderScoreboard() {
    scoreboardList.innerHTML = "";
    const standings = state.roster
        .map((player, index) => ({ player, index }))
        .sort((a, b) => b.player.score - a.player.score || a.index - b.index);

    standings.forEach((entry, rank) => {
        const row = document.createElement("div");
        row.className = "score-row";
        if (!entry.player.active) {
            row.classList.add("inactive");
        }

        const place = document.createElement("span");
        place.className = "score-rank";
        place.textContent = `#${rank + 1}`;

        const identity = document.createElement("div");
        identity.className = "score-player";
        const name = document.createElement("span");
        name.className = "score-name";
        name.textContent = entry.player.name;
        identity.appendChild(name);

        const playedThisRound = state.players.some(player => player.id === entry.player.id);
        if (!entry.player.active || !playedThisRound) {
            const status = document.createElement("span");
            status.className = "score-status";
            status.textContent = entry.player.active ? "Vòng sau" : "Đã rời bàn";
            identity.appendChild(status);
        }

        const score = document.createElement("span");
        score.className = "score-value";
        score.textContent = `${entry.player.score} điểm`;

        row.append(place, identity, score);
        scoreboardList.appendChild(row);
    });
}

function renderSummary() {
    // Topic header
    summaryCategoryTag.textContent = state.currentCategory;
    summaryCivilianWord.textContent = state.civilianWord;
    summarySpyWord.textContent = state.spyWord;
    summaryRoundOutcome.textContent = state.roundOutcome;
    renderScoreboard();
    
    // Player grid list
    summaryList.innerHTML = "";
    state.players.forEach(p => {
        const row = document.createElement("div");
        row.className = `summary-row role-${p.role}`;
        
        let roleLabel = "";
        let roleIcon = "";
        if (p.role === "civilian") {
            roleLabel = "Dân Thường";
            roleIcon = "🧑‍🌾";
        } else if (p.role === "spy") {
            roleLabel = "Gián Điệp";
            roleIcon = "🕵️";
        } else if (p.role === "blank") {
            roleLabel = "Dân Trắng";
            roleIcon = "🤍";
        }

        const identity = document.createElement("div");
        identity.className = "summary-identity";
        const avatar = document.createElement("span");
        avatar.className = "summary-avatar";
        avatar.textContent = roleIcon;
        const name = document.createElement("span");
        name.className = "summary-name";
        name.textContent = p.name;
        identity.append(avatar, name);

        const roleCard = document.createElement("div");
        roleCard.className = "summary-role-card";
        const role = document.createElement("span");
        role.className = "role-tag";
        role.textContent = roleLabel;
        const word = document.createElement("span");
        word.className = "summary-word";
        word.textContent = p.role === "blank" ? "Không có từ" : p.word;
        roleCard.append(role, word);

        row.append(identity, roleCard);
        summaryList.appendChild(row);
    });
    
}

// End Game & Show Summary Grid
function endGame() {
    soundEffects.playReveal();
    renderSummary();
    screens.show(screens.summary);
    saveCachedMatch("summary");
}

function showResumePrompt(snapshot) {
    pendingCachedMatch = snapshot;
    resumeModal.classList.add("visible");
    resumeModal.setAttribute("aria-hidden", "false");
}

function hideResumePrompt() {
    resumeModal.classList.remove("visible");
    resumeModal.setAttribute("aria-hidden", "true");
}

function restoreCachedMatch() {
    const snapshot = pendingCachedMatch;
    if (!snapshot) return;

    state.roster = snapshot.roster;
    state.nextPlayerId = snapshot.nextPlayerId;
    state.players = snapshot.players;
    state.revealIndex = snapshot.revealIndex;
    state.playedClusterIds = new Set(snapshot.playedClusterIds || []);
    state.currentCategory = snapshot.currentCategory;
    state.currentClusterTheme = snapshot.currentClusterTheme;
    state.civilianWord = snapshot.civilianWord;
    state.spyWord = snapshot.spyWord;
    state.speakingOrder = snapshot.speakingOrder;
    state.roundOutcome = snapshot.roundOutcome || "";
    state.roundResolved = Boolean(snapshot.roundResolved);
    state.spyGuessMode = snapshot.spyGuessMode || null;
    state.outcomeDialog = snapshot.outcomeDialog || null;
    blankChance.value = snapshot.blankChance || "0";

    hideResumePrompt();
    pendingCachedMatch = null;

    if (snapshot.phase === "reveal") {
        setupNextPlayerReveal();
        screens.show(screens.reveal);
    } else if (snapshot.phase === "play") {
        renderPlayBoard();
        screens.show(screens.play);
        if (state.outcomeDialog) {
            showOutcomeModal(
                state.outcomeDialog.title,
                state.outcomeDialog.message,
                state.outcomeDialog.needsSpyGuess,
                state.outcomeDialog.needsSpyConfirmation
            );
        }
    } else {
        renderSummary();
        screens.show(screens.summary);
    }
}

function beginNewMatch() {
    clearCachedMatch();
    pendingCachedMatch = null;
    hideResumePrompt();
    screens.show(screens.setup);
}

function setSettingsMessage(message = "", isError = false) {
    settingsMessage.textContent = message;
    settingsMessage.classList.toggle("visible", Boolean(message));
    settingsMessage.classList.toggle("error", isError);
}

function renderSettingsPlayers() {
    settingsPlayerList.innerHTML = "";
    const activeCount = getActiveRoster().length;
    settingsActiveCount.textContent = `${activeCount} đang chơi`;

    state.roster.forEach(player => {
        const row = document.createElement("div");
        row.className = "settings-player-row";
        if (!player.active) {
            row.classList.add("inactive");
        }

        const details = document.createElement("div");
        details.className = "settings-player-details";
        const name = document.createElement("span");
        name.className = "settings-player-name";
        name.textContent = player.name;
        const score = document.createElement("span");
        score.className = "settings-player-score";
        score.textContent = player.active ? `${player.score} điểm` : `${player.score} điểm - đã rời bàn`;
        details.append(name, score);

        const action = document.createElement("button");
        action.className = player.active ? "settings-remove-btn" : "settings-restore-btn";
        action.type = "button";
        action.textContent = player.active ? "Xoá" : "Thêm lại";
        action.disabled = player.active && activeCount <= 3;
        action.addEventListener("click", () => toggleRosterPlayer(player.id));

        row.append(details, action);
        settingsPlayerList.appendChild(row);
    });
}

function openSettings() {
    settingsBlankChance.value = blankChance.value;
    setSettingsMessage();
    renderSettingsPlayers();
    settingsModal.classList.add("visible");
    settingsModal.setAttribute("aria-hidden", "false");
}

function closeSettings() {
    settingsModal.classList.remove("visible");
    settingsModal.setAttribute("aria-hidden", "true");
    settingsNewPlayer.value = "";
    setSettingsMessage();
}

function toggleRosterPlayer(playerId) {
    const player = state.roster.find(entry => entry.id === playerId);
    if (!player) return;

    if (player.active && getActiveRoster().length <= 3) {
        setSettingsMessage("Cần ít nhất 3 người chơi cho vòng kế tiếp.", true);
        return;
    }

    player.active = !player.active;
    setSettingsMessage(`${player.name} sẽ ${player.active ? "tham gia" : "rời bàn"} từ vòng kế tiếp.`);
    renderSettingsPlayers();
    saveActiveNames();
    saveCachedMatch();
    if (screens.summary.classList.contains("active")) {
        renderScoreboard();
    }
}

function addRosterPlayer(event) {
    event.preventDefault();
    const name = settingsNewPlayer.value.trim();
    const duplicated = state.roster.some(player =>
        player.name.localeCompare(name, "vi", { sensitivity: "base" }) === 0
    );

    if (!name) {
        setSettingsMessage("Vui lòng nhập tên người chơi.", true);
        return;
    }
    if (duplicated) {
        setSettingsMessage("Tên này đã có trên bảng điểm. Hãy dùng nút Thêm lại nếu cần.", true);
        return;
    }

    state.roster.push(createRosterPlayer(name));
    settingsNewPlayer.value = "";
    setSettingsMessage(`${name} sẽ tham gia từ vòng kế tiếp.`);
    renderSettingsPlayers();
    saveActiveNames();
    saveCachedMatch();
    if (screens.summary.classList.contains("active")) {
        renderScoreboard();
    }
}

// Next Round handler
function triggerNextRound() {
    soundEffects.playClick();
    assignRolesAndWords();
    determineSpeakingOrder();
    state.revealIndex = 0;
    setupNextPlayerReveal();
    screens.show(screens.reveal);
    saveCachedMatch("reveal");
}

// Setup Event Listeners
function setupEventListeners() {
    textareaNames.addEventListener("input", updatePlayerCount);
    
    blankChance.addEventListener("change", () => soundEffects.playClick());
    settingsBlankChance.addEventListener("change", () => {
        blankChance.value = settingsBlankChance.value;
        soundEffects.playClick();
        saveCachedMatch();
    });
    btnOpenSettings.addEventListener("click", openSettings);
    btnCloseSettings.addEventListener("click", closeSettings);
    btnSettingsDone.addEventListener("click", closeSettings);
    settingsAddPlayerForm.addEventListener("submit", addRosterPlayer);
    btnResumeMatch.addEventListener("click", restoreCachedMatch);
    btnNewMatch.addEventListener("click", beginNewMatch);
    
    // Game button triggers
    btnStart.addEventListener("click", startGame);
    
    // Reveal card events
    cardContainer.addEventListener("click", handleCardRevealToggle);
    btnRevealAction.addEventListener("click", handleCardRevealToggle);
    
    btnSpyClaim.addEventListener("click", promptVoluntarySpyGuess);
    btnConfirmSpyClaim.addEventListener("click", beginVoluntarySpyGuess);
    btnCancelSpyClaim.addEventListener("click", cancelVoluntarySpyGuess);
    btnSpyCorrect.addEventListener("click", () => resolveSpyGuess(true));
    btnSpyWrong.addEventListener("click", () => resolveSpyGuess(false));
    btnShowSummary.addEventListener("click", endGame);
    
    // Next round trigger
    btnNextRound.addEventListener("click", triggerNextRound);
}

// Restore saved players names from localStorage
function restoreSavedState() {
    const savedNames = localStorage.getItem("spygame_names");
    if (savedNames) {
        textareaNames.value = savedNames;
    } else {
        textareaNames.value = "Thủy\nGiáo\nCường\nTrường\nTrân";
    }
    updatePlayerCount();
    
    const savedPlayedIds = localStorage.getItem("spygame_played_ids");
    if (savedPlayedIds) {
        try {
            state.playedClusterIds = new Set(JSON.parse(savedPlayedIds));
        } catch (e) {
            state.playedClusterIds = new Set();
        }
    }
}

// App Startup
document.addEventListener("DOMContentLoaded", async () => {
    setupEventListeners();
    restoreSavedState();
    await loadDatabase();

    screens.show(screens.setup);
    if (state.databaseStatus === "ready") {
        const cachedMatch = loadCachedMatch();
        if (cachedMatch) {
            showResumePrompt(cachedMatch);
        }
    }
});
