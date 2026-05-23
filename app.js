// Fallback Word Database of exactly 2-syllable Vietnamese word pairs
const FALLBACK_WORDS = {
    "version": "2.0",
    "language": "vi",
    "categories": [
        {
            "id": "food_vn",
            "name": "Món Việt",
            "icon": "🍜",
            "clusters": [
                { "theme": "Bánh mặn", "words": ["Bánh mì", "Bánh bao", "Bánh chưng", "Bánh tét", "Bánh xèo"] },
                { "theme": "Món nước", "words": ["Phở bò", "Bún bò", "Hủ tiếu", "Mì Quảng", "Bún riêu"] },
                { "theme": "Cơm mặn", "words": ["Cơm tấm", "Cơm rang", "Cơm gà", "Cơm cháy", "Cơm lam"] },
                { "theme": "Nem cuốn", "words": ["Gỏi cuốn", "Chả giò", "Nem nướng", "Bò cuốn", "Bì cuốn"] }
            ]
        },
        {
            "id": "drinks",
            "name": "Đồ uống",
            "icon": "🥤",
            "clusters": [
                { "theme": "Đồ uống ngọt", "words": ["Trà sữa", "Cà phê", "Sinh tố", "Nước ép", "Bạc xỉu"] },
                { "theme": "Đồ giải khát", "words": ["Nước mía", "Nước dừa", "Trà đá", "Sữa đậu", "Nước sâm"] },
                { "theme": "Nước uống có ga", "words": ["Bia lon", "Nước ngọt", "Rượu vang", "Soda chanh", "Sữa chua"] }
            ]
        },
        {
            "id": "vehicles",
            "name": "Phương tiện",
            "icon": "🚗",
            "clusters": [
                { "theme": "Xe đường bộ", "words": ["Xe máy", "Xe đạp", "Ô tô", "Xe buýt", "Xích lô"] },
                { "theme": "Phương tiện lớn", "words": ["Tàu hỏa", "Máy bay", "Tàu thủy", "Du thuyền", "Cáp treo"] }
            ]
        },
        {
            "id": "places",
            "name": "Địa điểm",
            "icon": "🏖️",
            "clusters": [
                { "theme": "Giải trí dã ngoại", "words": ["Bãi biển", "Hồ bơi", "Công viên", "Rạp phim", "Vườn thú"] },
                { "theme": "Địa điểm thường nhật", "words": ["Trường học", "Bệnh viện", "Chợ búa", "Siêu thị", "Cửa hàng"] }
            ]
        },
        {
            "id": "objects",
            "name": "Đồ vật",
            "icon": "🔧",
            "clusters": [
                { "theme": "Dụng cụ viết", "words": ["Bút chì", "Bút bi", "Bút mực", "Thước kẻ", "Tẩy chì"] },
                { "theme": "Đồ dùng ăn uống", "words": ["Thìa sứ", "Đũa tre", "Bát cơm", "Đĩa nhựa", "Cốc nước"] },
                { "theme": "Thiết bị học tập/làm việc", "words": ["Sách vở", "Bàn học", "Ghế gỗ", "Bảng đen", "Cặp sách"] }
            ]
        },
        {
            "id": "body",
            "name": "Cơ thể người",
            "icon": "🫀",
            "clusters": [
                { "theme": "Bộ phận trên mặt", "words": ["Đôi mắt", "Cái mũi", "Đôi tai", "Đôi môi", "Mái tóc"] },
                { "theme": "Bộ phận vận động", "words": ["Đôi tay", "Đôi chân", "Bả vai", "Đầu gối", "Cổ tay"] }
            ]
        },
        {
            "id": "tech",
            "name": "Công nghệ",
            "icon": "📱",
            "clusters": [
                { "theme": "Thiết bị cá nhân", "words": ["Điện thoại", "Laptop", "Ipad", "Tai nghe", "Loa kéo"] }
            ]
        },
        {
            "id": "clothing",
            "name": "Thời trang",
            "icon": "👗",
            "clusters": [
                { "theme": "Trang phục hàng ngày", "words": ["Áo thun", "Áo len", "Quần jean", "Váy cưới", "Áo khoác"] }
            ]
        },
        {
            "id": "nature",
            "name": "Thiên nhiên",
            "icon": "🌿",
            "clusters": [
                { "theme": "Thiên thể vũ trụ", "words": ["Mặt trăng", "Mặt trời", "Ngôi sao", "Hành tinh", "Vũ trụ"] },
                { "theme": "Hiện tượng thời tiết", "words": ["Mưa rào", "Bão lớn", "Nắng gắt", "Sương mù", "Gió lốc"] }
            ]
        },
        {
            "id": "school",
            "name": "Trường học",
            "icon": "📚",
            "clusters": [
                { "theme": "Môn học tự nhiên", "words": ["Toán học", "Vật lý", "Hóa học", "Sinh học", "Tin học"] }
            ]
        }
    ]
};

// Application State
const state = {
    wordDatabase: null,
    players: [],            // Array of { name, role, word }
    revealIndex: 0,
    playedClusterIds: new Set(),
    currentCategory: "",
    currentClusterTheme: "",
    civilianWord: "",
    spyWord: "",
    speakingOrder: [],
    timerInterval: null,
    timerSeconds: 0
};

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
    }
};

// DOM Elements
const textareaNames = document.getElementById("names-input");
const countBadge = document.getElementById("names-count");
const warningAlert = document.getElementById("warning-alert");
const warningText = document.getElementById("warning-text");

const spyVal = document.getElementById("spy-val");
const blankVal = document.getElementById("blank-val");
const spyMinus = document.getElementById("spy-minus");
const spyPlus = document.getElementById("spy-plus");
const blankMinus = document.getElementById("blank-minus");
const blankPlus = document.getElementById("blank-plus");

const btnStart = document.getElementById("btn-start");

// Reveal Phase Elements
const revealName = document.getElementById("reveal-player-name");
const revealPrompt = document.getElementById("reveal-prompt");
const cardContainer = document.getElementById("card-container");
const cardBack = document.getElementById("card-back");
const cardRoleBadge = document.getElementById("card-role-badge");
const cardWordVal = document.getElementById("card-word-val");
const cardBottomInstruction = document.getElementById("card-bottom-instruction");
const btnRevealAction = document.getElementById("btn-reveal-action");

// Play Board Elements
const speakingList = document.getElementById("speaking-list");
const timerVal = document.getElementById("timer-val");
const btnTimerPlay = document.getElementById("timer-play-btn");
const btnTimerPause = document.getElementById("timer-pause-btn");
const btnTimerReset = document.getElementById("timer-reset-btn");
const btnEndGame = document.getElementById("btn-end-game");

// Summary Elements
const summaryCategoryTag = document.getElementById("summary-category");
const summaryCivilianWord = document.getElementById("summary-civilian-word");
const summarySpyWord = document.getElementById("summary-spy-word");
const summaryList = document.getElementById("summary-list");
const btnNextRound = document.getElementById("btn-next-round");

// Initialization & Database loading
async function loadDatabase() {
    try {
        const response = await fetch("./data/words.json");
        if (response.ok) {
            state.wordDatabase = await response.json();
            console.log("📡 SpyGame: Loaded AI word database successfully!");
        } else {
            throw new Error("Could not fetch words.json");
        }
    } catch (e) {
        console.warn("⚠️ SpyGame: Falling back to built-in words list because local words.json was not found.");
        state.wordDatabase = FALLBACK_WORDS;
    }
}

// Extract player names from textarea
function getPlayerNames() {
    return textareaNames.value
        .split("\n")
        .map(name => name.trim())
        .filter(name => name.length > 0);
}

// Auto-updates player names badge
function updatePlayerCount() {
    const names = getPlayerNames();
    countBadge.textContent = `${names.length} người`;
    validateConfig();
}

// Configuration handlers (Spies & Blanks)
function handleConfigChange(type, change) {
    soundEffects.playClick();
    if (type === "spy") {
        let val = parseInt(spyVal.textContent) + change;
        if (val < 1) val = 1;
        spyVal.textContent = val;
    } else if (type === "blank") {
        let val = parseInt(blankVal.textContent) + change;
        if (val < 0) val = 0;
        blankVal.textContent = val;
    }
    validateConfig();
}

// Configuration validation
function validateConfig() {
    const names = getPlayerNames();
    const n = names.length;
    const s = parseInt(spyVal.textContent);
    const b = parseInt(blankVal.textContent);
    
    if (n < 3) {
        showWarning("Trò chơi cần ít nhất 3 người chơi để bắt đầu.");
        btnStart.disabled = true;
        return false;
    }
    
    if (s + b >= n) {
        showWarning(`Tổng số Gián điệp (${s}) và Dân trắng (${b}) phải nhỏ hơn tổng số người chơi (${n}).`);
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

// Role Assignor Engine
function assignRolesAndWords() {
    const names = getPlayerNames();
    const total = names.length;
    const sCount = parseInt(spyVal.textContent);
    const bCount = parseInt(blankVal.textContent);
    
    selectWordPair();
    
    // Build role pool
    const roles = [];
    for (let i = 0; i < sCount; i++) roles.push("spy");
    for (let i = 0; i < bCount; i++) roles.push("blank");
    while (roles.length < total) roles.push("civilian");
    
    shuffleArray(roles);
    
    // Assign to players
    state.players = names.map((name, idx) => {
        const role = roles[idx];
        let word = "";
        if (role === "civilian") {
            word = state.civilianWord;
        } else if (role === "spy") {
            word = state.spyWord;
        } else if (role === "blank") {
            word = "???"; // Blank players don't know the word
        }
        return { name, role, word };
    });
}

// 3% Blank Rule implementation for choosing who speaks first
function determineSpeakingOrder() {
    const total = state.players.length;
    
    // Find player index categories
    const blanks = [];
    const others = [];
    
    state.players.forEach((p, idx) => {
        if (p.role === "blank") {
            blanks.push(idx);
        } else {
            others.push(idx);
        }
    });
    
    let firstSpeakerIdx = -1;
    
    // 3% safety rule for Blanks
    if (blanks.length > 0 && Math.random() <= 0.03) {
        firstSpeakerIdx = blanks[Math.floor(Math.random() * blanks.length)];
    } else if (others.length > 0) {
        firstSpeakerIdx = others[Math.floor(Math.random() * others.length)];
    } else {
        // Fallback safety
        firstSpeakerIdx = Math.floor(Math.random() * total);
    }
    
    // Shuffling remaining players
    const remaining = [];
    for (let i = 0; i < total; i++) {
        if (i !== firstSpeakerIdx) remaining.push(i);
    }
    shuffleArray(remaining);
    
    state.speakingOrder = [firstSpeakerIdx, ...remaining];
}

// Start Game Event
function startGame() {
    if (!validateConfig()) return;
    
    soundEffects.playReveal();
    
    // Save names to local storage for persistence
    const names = getPlayerNames();
    localStorage.setItem("spygame_names", names.join("\n"));
    
    assignRolesAndWords();
    determineSpeakingOrder();
    
    // Setup reveal phase
    state.revealIndex = 0;
    setupNextPlayerReveal();
    screens.show(screens.reveal);
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
        cardWordVal.textContent = p.word;
        cardBottomInstruction.textContent = "Hãy mô tả từ này thật khéo léo để tìm ra Gián điệp, tránh Dân trắng phát hiện ra từ!";
    } else if (p.role === "spy") {
        cardBack.classList.add("role-spy");
        cardRoleBadge.textContent = "Gián Điệp 🕵️";
        cardWordVal.textContent = p.word;
        cardBottomInstruction.textContent = "Mô tả từ này sao cho hòa nhập vào số đông. Cố gắng đoán từ của Dân thường!";
    } else if (p.role === "blank") {
        cardBack.classList.add("role-blank");
        cardRoleBadge.textContent = "Dân Trắng 🤍";
        cardWordVal.textContent = "Trống Trơn";
        cardBottomInstruction.textContent = "Bạn không có từ nào cả! Lắng nghe mọi người xung quanh mô tả để đoán xem từ bí mật là gì!";
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
            } else {
                initPlayBoard();
                screens.show(screens.play);
            }
        }, 300);
    }
}

// Gameplay Board (Speaking order + timer) Setup
function initPlayBoard() {
    speakingList.innerHTML = "";
    
    state.speakingOrder.forEach((pIdx, orderNum) => {
        const player = state.players[pIdx];
        const row = document.createElement("div");
        row.className = "speaker-row";
        if (orderNum === 0) row.classList.add("first-speaker");
        
        row.innerHTML = `
            <div class="speaker-num">${orderNum + 1}</div>
            <div class="speaker-name">${player.name}</div>
            <span class="speaker-tag">${orderNum === 0 ? "Nói đầu" : "Lượt sau"}</span>
        `;
        speakingList.appendChild(row);
    });
    
    // Reset turn timer
    resetTimer();
    startTimer();
}

// Timer Widget Logic
function startTimer() {
    clearInterval(state.timerInterval);
    btnTimerPlay.style.display = "none";
    btnTimerPause.style.display = "flex";
    
    state.timerInterval = setInterval(() => {
        state.timerSeconds++;
        const mins = String(Math.floor(state.timerSeconds / 60)).padStart(2, "0");
        const secs = String(state.timerSeconds % 60).padStart(2, "0");
        timerVal.textContent = `${mins}:${secs}`;
    }, 1000);
}

function pauseTimer() {
    clearInterval(state.timerInterval);
    btnTimerPause.style.display = "none";
    btnTimerPlay.style.display = "flex";
}

function resetTimer() {
    clearInterval(state.timerInterval);
    state.timerSeconds = 0;
    timerVal.textContent = "00:00";
    btnTimerPause.style.display = "none";
    btnTimerPlay.style.display = "flex";
}

// End Game & Show Summary Grid
function endGame() {
    soundEffects.playReveal();
    pauseTimer();
    
    // Topic header
    summaryCategoryTag.textContent = state.currentCategory;
    summaryCivilianWord.textContent = state.civilianWord;
    summarySpyWord.textContent = state.spyWord;
    
    // Player grid list
    summaryList.innerHTML = "";
    state.players.forEach(p => {
        const row = document.createElement("div");
        row.className = `summary-row role-${p.role}`;
        
        let roleLabel = "";
        if (p.role === "civilian") roleLabel = "Dân Thường";
        else if (p.role === "spy") roleLabel = "Gián Điệp";
        else if (p.role === "blank") roleLabel = "Dân Trắng";
        
        row.innerHTML = `
            <div class="summary-name">${p.name}</div>
            <div class="summary-role-card">
                <span class="role-tag">${roleLabel}</span>
                <span class="summary-word">${p.role === 'blank' ? '🤍 Không có' : p.word}</span>
            </div>
        `;
        summaryList.appendChild(row);
    });
    
    screens.show(screens.summary);
}

// Next Round handler
function triggerNextRound() {
    soundEffects.playClick();
    assignRolesAndWords();
    determineSpeakingOrder();
    state.revealIndex = 0;
    setupNextPlayerReveal();
    screens.show(screens.reveal);
}

// Setup Event Listeners
function setupEventListeners() {
    textareaNames.addEventListener("input", updatePlayerCount);
    
    // Config items plus/minus
    spyMinus.addEventListener("click", () => handleConfigChange("spy", -1));
    spyPlus.addEventListener("click", () => handleConfigChange("spy", 1));
    blankMinus.addEventListener("click", () => handleConfigChange("blank", -1));
    blankPlus.addEventListener("click", () => handleConfigChange("blank", 1));
    
    // Game button triggers
    btnStart.addEventListener("click", startGame);
    
    // Reveal card events
    cardContainer.addEventListener("click", handleCardRevealToggle);
    btnRevealAction.addEventListener("click", handleCardRevealToggle);
    
    // Play timer events
    btnTimerPlay.addEventListener("click", startTimer);
    btnTimerPause.addEventListener("click", pauseTimer);
    btnTimerReset.addEventListener("click", resetTimer);
    
    btnEndGame.addEventListener("click", endGame);
    
    // Next round trigger
    btnNextRound.addEventListener("click", triggerNextRound);
}

// Restore saved players names from localStorage
function restoreSavedState() {
    const savedNames = localStorage.getItem("spygame_names");
    if (savedNames) {
        textareaNames.value = savedNames;
        updatePlayerCount();
    }
    
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
    
    // Clean transition from load state to active UI
    screens.show(screens.setup);
});
