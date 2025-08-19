"""Prompts for the results parser agent."""


def get_initial_message(input_path: str, target_metrics: list[str]) -> str:
    """Get the initial message for the agent."""
    return f"""I need you to parse benchmark results from the directory: {input_path}

## TARGET METRICS
Extract these specific metrics: {target_metrics}

## CRITICAL REQUIREMENT: EXTRACT ONLY REAL DATA
You MUST process EVERY SINGLE .txt file in the directory structure and extract ALL metrics from ALL files. BUT ONLY extract data that actually exists - NEVER create fake data.

## METRIC VALIDATION REQUIREMENT
**BEFORE EXTRACTING ANY DATA, you MUST validate that ALL requested metrics exist:**
1. Use `execute_command` "grep -r 'METRIC_NAME' {input_path}/" for each target metric (replace METRIC_NAME with actual metric)
2. **ONLY proceed if ALL requested metrics are found in the data**
3. **If ANY requested metric is missing, return COMPLETELY EMPTY results with NO structure**
4. **NEVER extract or map to similar metrics - only exact matches**
5. **NEVER create placeholder values like 'N/A' - if metric doesn't exist, don't include it**

## YOUR WORKFLOW - FOLLOW THESE STEPS IN ORDER:

### STEP 1: METRIC VALIDATION (REQUIRED FIRST STEP)
**YOU MUST VALIDATE ALL METRICS BEFORE PROCEEDING**
For each target metric, execute these commands:
1. Use `execute_command` "grep -r 'METRIC_NAME' {input_path}/" to check if metric exists (replace METRIC_NAME with actual metric)
2. Use `execute_command` "find {input_path} -name '*.txt' -exec grep -H 'METRIC_NAME' {{}} \\;" to get all files with each metric
3. **ONLY continue if ALL requested metrics are found**
4. **If ANY metric is missing, return COMPLETELY EMPTY results: {{"iterations": []}}**

### STEP 2: DISCOVER ACTUAL FILES (ONLY IF VALIDATION PASSES)
1. Use `scan_input` to understand the directory structure
2. Use `execute_command` "find . -type f -name '*.txt'" to find ALL text files
3. Use `execute_command` "find {input_path} -type d" to understand hierarchy
4. Use `execute_command` "ls -R {input_path}" to see complete directory structure
5. **ONLY work with files that actually exist**

### STEP 3: EXTRACT FROM ACTUAL FILES ONLY
**YOU MUST EXTRACT FROM EVERY SINGLE .TXT FILE**
For each target metric, execute these commands:
1. Use `execute_command` "find {input_path} -name '*.txt' -type f" to list ALL text files
2. Use `execute_command` "grep -r 'METRIC_NAME' {input_path}/" to find ALL occurrences (replace METRIC_NAME with actual metric)
3. Use `execute_command` "find {input_path} -name '*.txt' -exec grep -H 'METRIC_NAME' {{}} \\;" to get ALL file paths with metric values
4. Use `execute_command` "cat filename.txt | grep 'METRIC_NAME'" for each file that contains the metric
5. Repeat steps 2-4 for each target metric
6. **ONLY extract values that actually exist in the files**

### STEP 4: BUILD JSON FROM REAL DATA ONLY
After getting ALL terminal outputs:
1. Parse the terminal command results from ALL files
2. Extract exact values from ALL file outputs
3. Map ALL file paths to runs/iterations/instances
4. Build the JSON structure with ONLY real data
5. Return the final structured JSON with ONLY real extracted values

## CRITICAL INSTRUCTIONS
- **VALIDATE FIRST**: You MUST validate ALL requested metrics exist before proceeding
- **EXACT MATCHES ONLY**: Only extract metrics with exact names as requested
- **NO MAPPING**: Never map "RPS" to "Requests/sec" or similar - only exact matches
- **FAIL GRACEFULLY**: If validation fails, return {{"iterations": []}} - NO structure, NO placeholders
- **NO PLACEHOLDERS**: Never use "N/A", "null", or any placeholder values
- **EXECUTE TOOLS FIRST**: You MUST use the tools to explore and extract data from ALL files
- **EXTRACT FROM ALL FILES**: Process EVERY .txt file in the directory structure
- **EXTRACT EXACT VALUES**: Never modify, round, or approximate numeric values
- **USE TERMINAL COMMANDS**: Prioritize `execute_command` for precise extraction
- **COPY PRECISELY**: Use exact values as they appear in files
- **VERIFY ACCURACY**: Double-check all extracted values against source files
- **NO EARLY STOPPING**: Do not stop after processing the first file - continue until ALL files are processed
- **COMPLETE STRUCTURE**: Build the complete JSON with ONLY real runs, iterations, and instances

## ANTI-HALLUCINATION RULES
- **NEVER CREATE FAKE DATA**: Do not invent runs, iterations, instances, or metrics that don't exist
- **NEVER CREATE FAKE VALUES**: Do not generate random numbers or placeholder values
- **NEVER CREATE FAKE DIRECTORIES**: Only include directories that actually exist in the file system
- **NEVER CREATE FAKE METRICS**: Only extract the exact metrics specified in target_metrics
- **NEVER MAP METRICS**: Do not map requested metrics to similar ones found in data
- **NEVER USE PLACEHOLDERS**: Do not use "N/A", "null", "undefined", or any placeholder text
- **USE TOOLS FIRST**: Always use scan_input and execute_command to discover what actually exists
- **VERIFY EXISTENCE**: Before including any data, verify it exists through tool outputs
- **MISSING DATA IS OK**: If data is missing, leave it out rather than inventing it

## TERMINAL COMMAND STRATEGY
- Use `execute_command` "grep -r 'EXACT_METRIC_NAME' {input_path}/" for precise metric search across ALL files
- Use `execute_command` "find {input_path} -name '*.txt' -exec grep -H 'EXACT_METRIC_NAME' {{}} \\;" to get ALL files with each metric
- Use `execute_command` "cat filename.txt | grep 'EXACT_METRIC_NAME'" for file-specific extraction
- Use `execute_command` "awk '/EXACT_METRIC_NAME/ {{print $0}}' filename.txt" for pattern matching
- Always use exact metric names as provided in the target_metrics list
- Do not modify metric names during search - use them exactly as specified

## VALUE INTEGRITY
- Extract exact numeric values from terminal command outputs for ALL files
- Do not generate, estimate, or approximate any values
- Use precise copy-paste for all numeric data
- Maintain exact decimal precision as found in source files
- **NEVER use placeholder values like "N/A", "null", or "undefined"**

## EXPECTED OUTPUT STRUCTURE
Your final JSON MUST include ONLY:
- **REAL ITERATIONS**: Only iterations that actually exist within each run
- **REAL INSTANCES**: Only instance files that actually exist within each iteration
- **REAL METRICS**: Only target metrics that are actually found in the files
- **REAL VALUES**: Only numeric values that are actually extracted from files

## FAILURE SCENARIO
If ANY requested metric is not found:
- Return EXACTLY: {{"iterations": []}}
- Do NOT create any structure
- Do NOT include any instances or statistics
- Do NOT use placeholder values
- Just return the empty structure

## CRITICAL SUCCESS CRITERIA
- ✅ Validate ALL requested metrics exist before proceeding
- ✅ Process ALL .txt files in the directory structure
- ✅ Extract metrics from EVERY file that contains them
- ✅ Build complete JSON structure with ONLY real iterations/instances
- ✅ Include ONLY real extracted values in the final output
- ✅ Maintain exact numeric precision from source files
- ✅ NEVER create fake data or invent values
- ✅ NEVER map metrics to similar ones - only exact matches
- ✅ NEVER use placeholder values - if metric doesn't exist, don't include it

## IMPORTANT: DO NOT RETURN JSON UNTIL YOU HAVE EXECUTED ALL TOOLS AND PROCESSED ALL FILES
Start by validating ALL requested metrics exist, then explore the directory structure and extract the target metrics with absolute precision from ALL files. Only return the final JSON after you have collected ALL the real data from ALL files. NEVER invent or create data that doesn't exist."""
