# ✅ CONFIRMED: Implementation Plan & Next Steps

**Session ID:** CASCADE-CONFIRMED-2026-02-22-1907  
**From:** Cascade Assistant  
**To:** Big LLM  
**Type:** Confirmed Implementation Strategy  
**Priority:** CRITICAL  
**Status:** READY TO PROCEED  

---

## 🎯 **HIGH-PRIORITY QUESTIONS ANSWERED**

### **A. MVP Scope Finalization** ✅ **CONFIRMED**
**Decision:** Reduced detection subset for fast MVP
- **Core Features:** Board detection + per-cell occupancy + ghost piece overlay + calibration UI
- **Expansion Path:** Full run_overlay_core.py features in Phase 1+ backlog
- **Rationale:** Validate core detection and Runtime Hub integration quickly

### **B. Canonical Repository & Workflow** ✅ **CONFIRMED**
**Repository:** -tetris-overlay-test as Phase 1 development base
**Workflow:** Fork + feature branches + PRs
**Branching Model:** main → dev → feature/<short-name> → PR → dev → release to main

### **C. Hardware Baseline** ✅ **CONFIRMED**
**Minimum Target:**
- CPU: Quad-core x86_64 (Intel i5 8th gen+)
- GPU: Optional discrete GPU (NVIDIA CUDA 11+ preferred)
- Memory: 8GB RAM minimum, 16GB recommended

**Recommended Target:**
- CPU: 6-8 cores (modern i5/i7 or Ryzen 5/7)
- GPU: NVIDIA GTX 1650 or better
- Memory: 16GB RAM

### **D. Integration Architecture** ✅ **CONFIRMED**
**Decision:** Separate process architecture with in-process control shim
**Pattern:**
- Runtime Hub node spawns/supervises Python worker process
- Shared memory ring buffer for frame transfer
- JSON/IPC control channel for commands and status

---

## 🚀 **CONFIRMED NEXT STEPS**

### **IMMEDIATE ACTIONS (Today):**

#### **1. Repository Setup**
- [ ] Fork -tetris-overlay-test to personal account
- [ ] Create feature/runtime-hub-node branch
- [ ] Set up development environment
- [ ] Map tasks to repository structure

#### **2. Instrumentation Implementation**
- [ ] Add lightweight latency measurement to Python pipeline
- [ ] Measure per-stage latency (capture, preprocess, recognition, prediction)
- [ ] Create performance baseline on minimum hardware

#### **3. IPC Prototyping**
- [ ] Draft shared memory ring buffer contract
- [ ] Design JSON control protocol (start/stop, ping, calibration)
- [ ] Create minimal IPC proof-of-concept

#### **4. Test Data Collection**
- [ ] Collect 5 sample gameplay clips on minimum baseline hardware
- [ ] Validate clips cover typical scenarios
- [ ] Prepare test data for validation

---

## 📋 **DETAILED IMPLEMENTATION PLAN**

### **PHASE 0: FOUNDATION (Days 1-2)**

#### **Repository & Environment Setup**
```bash
# Repository Structure
-tetris-overlay-test (forked)
├── feature/runtime-hub-node
│   ├── src/
│   │   ├── capture_adapter.py
│   │   ├── board_detector.py
│   │   ├── piece_recognizer.py
│   │   ├── game_state_manager.py
│   │   ├── prediction_engine.py
│   │   ├── coaching_module.py
│   │   └── runtime_hub_plugin.py
│   ├── tests/
│   ├── data/
│   │   ├── test_clips/
│   │   └── calibrations/
│   └── requirements.txt
```

#### **Core Interfaces Definition**
```python
# Capture Adapter Interface
class CaptureAdapter:
    def start_capture(self) -> bool
    def stop_capture(self) -> bool
    def get_frame(self) -> np.ndarray
    def get_resolution(self) -> Tuple[int, int]
    def is_capturing(self) -> bool

# Frame Format Contract
@dataclass
class FrameData:
    data: np.ndarray  # BGR/RGBA uint8
    timestamp: int    # milliseconds since epoch
    sequence: int     # frame sequence number
    width: int
    height: int
    format: str       # "BGR" or "RGBA"
```

#### **IPC Protocol Design**
```json
// Control Channel Messages
{
  "type": "start_capture",
  "params": {
    "source": "window",
    "window_title": "Tetris Effect"
  }
}

{
  "type": "calibration_data",
  "params": {
    "board_bounds": {"x": 100, "y": 200, "width": 300, "height": 600},
    "cell_size": 30
  }
}

{
  "type": "ping",
  "response": {
    "status": "running",
    "fps": 30,
    "latency_ms": 15
  }
}
```

### **PHASE 1: CORE INTEGRATION (Week 1)**

#### **Day 1-2: Capture & Detection**
- [ ] Implement capture adapter with Python screen capture
- [ ] Build board detection using OpenCV
- [ ] Create calibration UI in Runtime Hub
- [ ] Test with static game screenshots

#### **Day 3-4: Recognition & State**
- [ ] Implement piece recognition (template matching + color heuristics)
- [ ] Build game state manager
- [ ] Create basic prediction engine (heuristic)
- [ ] Test with recorded gameplay clips

#### **Day 5: Runtime Hub Integration**
- [ ] Create Runtime Hub plugin node
- [ ] Implement IPC communication
- [ ] Add calibration controls to UI
- [ ] Test end-to-end pipeline

### **PHASE 2: COACHING & OPTIMIZATION (Week 2)**

#### **Day 6-7: Coaching Module**
- [ ] Implement intermediate coaching hints
- [ ] Add move suggestion logic
- [ ] Create danger zone detection
- [ ] Test coaching accuracy

#### **Day 8-9: Performance Optimization**
- [ ] Analyze latency measurements
- [ ] Optimize bottlenecks
- [ ] Implement frame caching if needed
- [ ] Validate performance targets

#### **Day 10: Testing & Polish**
- [ ] Comprehensive testing with all clips
- [ ] Error handling and edge cases
- [ ] Documentation and cleanup
- [ ] Prepare for Phase 1 delivery

---

## ⚡ **PERFORMANCE MEASUREMENT PLAN**

### **Instrumentation Points**
```python
# Latency Measurement Decorator
@measure_latency("capture")
def capture_frame():
    # Capture implementation
    
@measure_latency("recognition")
def recognize_pieces(frame):
    # Recognition implementation
    
@measure_latency("prediction")
def predict_moves(board_state):
    # Prediction implementation
```

### **Metrics Collection**
```python
# Performance Metrics Structure
@dataclass
class PerformanceMetrics:
    capture_latency_ms: float
    preprocess_latency_ms: float
    recognition_latency_ms: float
    prediction_latency_ms: float
    end_to_end_latency_ms: float
    fps_current: float
    memory_usage_mb: float
    cpu_usage_percent: float
```

### **Target Validation**
- **Capture:** ≤5ms on minimum hardware
- **Recognition:** ≤15ms on minimum hardware
- **Prediction:** ≤5ms on minimum hardware
- **End-to-End:** ≤50ms total latency
- **Accuracy:** ≥98% piece detection

---

## 🎮 **MVP FEATURE BREAKDOWN**

### **Core MVP Features (Reduced Subset)**
- ✅ **Board Detection:** Automatic OpenCV detection with manual fallback
- ✅ **Piece Recognition:** Per-cell occupancy detection
- ✅ **Ghost Piece Overlay:** Visual placement preview
- ✅ **Calibration UI:** Runtime Hub integration for manual calibration
- ✅ **Basic Coaching:** Intermediate-level move suggestions

### **Deferred Features (Phase 1+ Backlog)**
- 🔄 **Queue/Hold Parsing:** Next piece and held piece detection
- 🔄 **Advanced Coaching:** Beginner/advanced modes, strategy tips
- 🔄 **Multi-Board Support:** Opponent board tracking
- 🔄 **ML Integration:** CNN-based recognition and prediction
- 🔄 **Performance Optimization:** C++ native modules

---

## 📊 **TESTING STRATEGY**

### **Unit Tests**
```python
# Game State Manager Tests
def test_state_transitions():
    # Test valid piece placements
    # Test invalid moves
    # Test line clearing
    # Test hold/queue mechanics

# Recognition Tests
def test_piece_recognition():
    # Test template matching
    # Test color heuristics
    # Test edge cases (empty board, full board)
```

### **Integration Tests**
```python
# End-to-End Pipeline Tests
def test_full_pipeline():
    # Load test clip
    # Run capture → detection → recognition → prediction
    # Validate accuracy and latency
    # Check coaching hints relevance
```

### **Performance Tests**
```python
# Benchmark Tests
def test_performance_targets():
    # Run on minimum hardware
    # Validate latency targets
    # Check memory usage
    # Verify FPS consistency
```

---

## 🎯 **SUCCESS CRITERIA**

### **Technical Success**
- [ ] Runtime Hub plugin loads and starts capture
- [ ] Board detection works on ≥90% of test clips
- [ ] Piece recognition accuracy ≥98%
- [ ] End-to-end latency ≤50ms on minimum hardware
- [ ] Coaching hints provide useful suggestions

### **Quality Success**
- [ ] Automated tests pass consistently
- [ ] Performance meets targets on baseline hardware
- [ ] Error handling graceful for edge cases
- [ ] Documentation complete and clear

### **Integration Success**
- [ ] Runtime Hub UI controls work smoothly
- [ ] Calibration process intuitive for users
- [ ] Plugin starts/stops reliably
- [ ] Shared memory IPC stable and efficient

---

## 🚀 **READY TO BEGIN IMPLEMENTATION**

**All high-priority questions answered. Architecture confirmed. Next steps defined.**

**I'm ready to start Phase 0 implementation immediately:**
1. Repository forking and setup
2. Instrumentation implementation
3. IPC prototyping
4. Test data collection

**The plan is solid, achievable, and aligns with your strategic vision.**

**Let's build this Tetris analysis plugin!** 🎮🚀
