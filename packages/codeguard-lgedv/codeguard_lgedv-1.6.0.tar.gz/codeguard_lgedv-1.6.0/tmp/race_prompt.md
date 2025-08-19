You are an expert C++ concurrency analyst.

Please use the `detect_races` tool to manually analyze the C++ files in the directory: /home/worker/src/code_test/race_condition/test_3.

Then provide your expert analysis of race conditions, focusing on:
- Shared state accessed by multiple threads
- Unprotected shared state modifications
- Missing synchronization mechanisms (mutexes, locks, atomics)
- Thread-unsafe patterns
- Deadlock scenarios
- Review thread creation and join/detach logic
- Check for lock-free and concurrent data structure usage
- Provide before/after code examples for fixes

IMPORTANT: Only list race conditions or deadlocks if there is clear evidence in the code that a variable or resource is accessed from multiple threads (e.g., thread creation, callback, or handler running on a different thread). Do not warn about cases that are only speculative or lack evidence. If no evidence is found, clearly state: 'No multi-threaded access detected for this variable in the current code.' This will help ensure the analysis focuses on real issues and avoids unnecessary or speculative warnings.

# Automated Findings (for your review):
## 📊 Analysis Metadata

**Target Directory:** `/home/worker/src/code_test/race_condition/test_3`
**Files Analyzed:** 2 C++ files



## 📁 Source Code Context

### 1. 📁 **race_member.cpp**
**Path**: `/home/worker/src/code_test/race_condition/test_3/race_member.cpp`
**Thread Usage**: 1 thread-related operations
**Thread Entry Points**:
- lambda (line 13)

```cpp
// race_member.cpp
#include <thread>
#include <vector>
#include <iostream>
#include "include/Counter.h"

int main() {
    Counter counter;
    counter.value = 0;
    counter.is_protected = false;
    std::vector<std::thread> threads;
    for (int i = 0; i < 4; ++i) {
        threads.emplace_back([&counter]() {
            for (int j = 0; j < 10000; ++j) {
                counter.increment();
            }
            counter.reset();
        });
    }
    for (auto& t : threads) t.join();
    std::cout << "Final value: " << counter.value << std::endl;
    return 0;
}

```

### 2. 📁 **Counter.cpp**
**Path**: `/home/worker/src/code_test/race_condition/test_3/Counter.cpp`
**Thread Entry Points**:
No detect thread entrypoint functions.

```cpp
// Counter.cpp
#include "include/Counter.h"

void Counter::increment() {
    this->value++;
}

void Counter::reset() {
    this->value = 0;
}

```



## 🔧 Please Provide
1. **Detailed Analysis**: Review each race condition with clear evidence and assess its validity
2. **Risk Assessment**: Categorize findings by severity and likelihood
3. **Synchronization Strategy**: Recommend appropriate locking mechanisms
4. **Code Examples**: Show before/after code with proper synchronization

**For each issue found, use this format:**

## 🚨 **RACE CONDITION #[number]**: [Brief Description]
**Type:** [data_race|deadlock|missing_sync]
**Severity:** [Critical|High|Medium|Low]
**Files Involved:** [list of files]
**Function Name:** [function name or global scope/unknown]
**Problem Description:** [explanation]
**Fix Recommendation:** [suggested solution]

Focus on actionable recommendations that can be immediately implemented.
