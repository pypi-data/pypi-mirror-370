You are an expert Linux C++ resource management analyst.

**Task:**
Analyze the C++ files in `/home/worker/src/code_test/resource_leak/test_1` for resource leaks using the `analyze_resources` tool.
Focus strictly on real, evidence-based issues. Do NOT include any hypothetical, speculative, or potential cases—report only resource leaks that are clearly demonstrated by the code and findings.

**Resource Types to Check:**
- File descriptors (open/close, FILE*/fclose)
- Sockets (socket/close, network connections)
- Memory mapping (mmap/munmap, shared memory cleanup)
- IPC (message queues, semaphores, shared memory detach)
- Directory handles (opendir/closedir)

**Instructions:**
- Only provide your expert analysis. Do NOT repeat the Automated Findings section.
- For each confirmed issue, use the format below.
- Propose refactored code for all relevant C++ files.
- Focus on actionable, immediately applicable recommendations.

# Automated Findings (for your review):
## 📊 **Analysis Metadata**

- **Directory**: `/home/worker/src/code_test/resource_leak/test_1`
- **Analysis Type**: Linux C++ Resource Leak Detection
- **Files Analyzed**: 1
- **Resource Operations Found**: 2
- **Cross-file Flows**: 0



## 📄 Relevant Code Context:

### 📁 leak_file.cpp
**Path**: `/home/worker/src/code_test/resource_leak/test_1/leak_file.cpp`
**Lines with leak Operations**: [5, 14]
```cpp
#include <cstdio>
#include <iostream>

void leak_file_descriptor() {
    FILE* f = fopen("test.txt", "w");
    if (f) {
        fprintf(f, "Resource leak example\n");
        // Quên không gọi fclose(f); => rò rỉ file descriptor
    }
}

void leak_fd_in_loop() {
    for (int i = 0; i < 10; ++i) {
        FILE* f = fopen("test_loop.txt", "w");
        if (f) {
            fprintf(f, "Loop %d\n", i);
            // Không đóng file => rò rỉ nhiều file descriptor
        }
    }
}

int main() {
    leak_file_descriptor();
    leak_fd_in_loop();
    return 0;
}
```



**For each issue, use this format:**
## 🚨 RESOURCE LEAK #[number]: [Brief Description]
- **Type:** [resource type]
- **Severity:** [Critical|High|Medium|Low]
- **Files Involved:** [list of files]
- **Location:** [function name or global scope/unknown]
- **Problem:** [explanation]
- **Current Code:** [show problematic code]
- **Fix Recommendation:** [suggested code or approach]

**Best Practices:**
- Suggest modern C++ approaches (RAII, smart pointers, std::fstream, etc.) where applicable.
- Recommend prevention strategies for future code.

Do NOT include any speculative, hypothetical, or potential warnings. Only analyze and report on actual, evidenced resource leaks found in the code and findings provided.
