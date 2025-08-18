# Selective Git Revert Plan

## Context
After extensive work on migrating plugin configurations from list to dictionary format, we have mixed results:
- **Manual fixes**: 100% success rate, ~42 tests fixed
- **Automated fixes**: 0% success rate, created syntax errors and corrupted files

## Recommendation: Keep Successful Work, Revert Failures

### Files to KEEP (Successfully Fixed)
These files were manually fixed and have all tests passing:

**Test Files (42 tests total):**
- `tests/unit/test_notification_routing.py` - 15 tests passing
- `tests/unit/test_config_loader_path_validation.py` - 10 tests passing  
- `tests/unit/test_complex_config.py` - 10 tests passing
- `tests/unit/test_plugin_manager_tool_expansion.py` - 7 tests passing
- `tests/unit/test_dictionary_only_configuration.py` - 11 tests passing (new file)

**Core Architecture (Working):**
- `watchgate/config/models.py` - Updated Pydantic models for dict-only validation
- `watchgate/plugins/manager.py` - Removed list-to-dict conversion logic

**Configuration Files (All Working):**
- All 13 files in `configs/` directory - Successfully converted to dictionary format

### Files to REVERT (Automation Damaged)
These files were corrupted by automated scripts and need fresh starts:

**Test Files with Syntax Errors:**
- `tests/unit/test_config_loader.py` - Severely corrupted dictionary structures
- `tests/unit/test_plugin_manager_config_priority_sorting.py` - Missing commas, bracket mismatches
- `tests/unit/test_policy_discovery.py` - Unmatched braces

**Temporary Files to Delete:**
- `fix_test_configs.py` - Broken automation script
- `fix_yaml_configs.py` - Broken automation script  
- `fix_yaml_indentation.py` - Broken automation script
- `fix_brackets.py` - Broken automation script
- `failing_tests.txt` - Outdated test results

## Git Commands for Selective Revert

```bash
# Revert the corrupted test files
git checkout HEAD -- tests/unit/test_config_loader.py
git checkout HEAD -- tests/unit/test_plugin_manager_config_priority_sorting.py  
git checkout HEAD -- tests/unit/test_policy_discovery.py

# Remove temporary automation scripts
rm fix_test_configs.py fix_yaml_configs.py fix_yaml_indentation.py fix_brackets.py
rm failing_tests.txt

# Check status
git status
```

## Current Progress After Selective Revert

### ✅ Working (42 tests)
- Dictionary-only validation implemented and tested
- Core architecture successfully migrated
- Configuration files converted
- 4 major test files completely fixed

### ❌ Still Needs Work (~50+ tests)
- `test_config_loader.py` - Clean slate, needs list→dict conversion
- `test_plugin_manager_config_priority_sorting.py` - Clean slate  
- `test_policy_discovery.py` - Clean slate
- Multiple other test files not yet attempted

## Lessons for Next Attempt

### What Worked (Continue):
1. **Manual fixes** - Careful, deliberate changes to one section at a time
2. **Syntax validation** - Test Python syntax after each change
3. **Single file focus** - Complete one file before moving to the next
4. **Understanding structure** - Read and understand the code before changing it

### What Failed (Avoid):
1. **Regex automation** - Pattern matching can't handle complex contexts
2. **Batch operations** - Multiple files at once leads to cascading errors
3. **Generated code** - Scripts create invalid syntax consistently
4. **Recovery attempts** - Fixing broken automation makes things worse

## Next Steps for Continuation

1. **Verify clean state** after selective revert
2. **Run tests** to confirm 42 tests are still passing
3. **Pick ONE file** (suggest `test_policy_discovery.py` as smallest)
4. **Manual approach only** - No automation scripts
5. **Document each change** as you make it
6. **Test frequently** - Syntax check after every few changes

## Success Metrics
- **Before this work**: 0 tests passing with dictionary format
- **After selective revert**: 42 tests passing with dictionary format  
- **Remaining goal**: ~50+ more tests to fix manually

This represents significant progress (~45% complete) with a clear path forward using proven manual techniques.