import os
import glob
import re

tables_dir = r"c:\Users\hanfa\Documents\DeepL_G2IADO\deep_learning_final_project\results\tables"
tex_files = glob.glob(os.path.join(tables_dir, "**/*.tex"), recursive=True)

def process_table(content):
    lines = content.split('\n')
    new_lines = []
    
    in_tabular = False
    header_processed = False
    data_row_idx = 0
    
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        
        if line_stripped.startswith(r'\begin{tabular}'):
            in_tabular = True
            header_processed = False
            data_row_idx = 0
            new_lines.append(line)
            continue
            
        if line_stripped.startswith(r'\end{tabular}'):
            in_tabular = False
            new_lines.append(line)
            continue
            
        if in_tabular:
            if line_stripped in [r'\toprule', r'\midrule', r'\bottomrule']:
                new_lines.append(r'\hline')
                if line_stripped == r'\midrule':
                    # after midrule, data rows begin
                    data_row_idx = 0
                continue
                
            # If it's a content row
            if line_stripped and not line_stripped.startswith('%'):
                if not header_processed:
                    # It's the header row
                    new_lines.append(r'\rowcolor{TableHeader}')
                    # Split by &
                    parts = line.split('&')
                    new_parts = []
                    for idx, part in enumerate(parts):
                        # extract text, keeping \\ at the end if it's the last part
                        if idx == len(parts) - 1:
                            m = re.match(r'(.*?)((\s*\\\\)?\s*)$', part)
                            text = m.group(1).strip()
                            tail = m.group(2)
                            new_parts.append(f' \\tblhead{{{text}}}{tail}')
                        else:
                            new_parts.append(f' \\tblhead{{{part.strip()}}} ')
                    new_lines.append('&'.join(new_parts).strip())
                    header_processed = True
                else:
                    # It's a data row
                    if data_row_idx % 2 == 1:
                        new_lines.append(r'\rowcolor{TableAlt}')
                    new_lines.append(line)
                    data_row_idx += 1
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    return '\n'.join(new_lines)

for fpath in tex_files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    new_content = process_table(content)
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print(f"Processed {fpath}")
