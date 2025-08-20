import re, os, glob

def parse_nbib_to_bibtex(nbib_content):
    entries = nbib_content.strip().split('\n\n')
    bib_entries = []

    for entry in entries:
        lines = entry.strip().split('\n')
        fields = {}
        current_tag = None

        for line in lines:
            if re.match(r'^([A-Z]{2}  - |[A-Z]{3} - |[A-Z]{4}- )', line):
                tag, value = line.split('- ', 1)
                tag = tag.strip()
                current_tag = tag
                fields.setdefault(tag, []).append(value.strip())
            elif line.startswith('      '):  # continuation line
                if current_tag:
                    fields[current_tag][-1] += ' ' + line.strip()

        # Generate BibTeX fields
        author_list = fields.get('AU', ['Unknown'])
        authors = ' and '.join(author_list)
        first_author_lastname = author_list[0].split(',')[0].lower().replace(" ", "") if author_list else 'unknown'
        year = fields.get('DP', ['n.d.'])[0][:4]

        # BibTeX key
        bibkey = f"{first_author_lastname}{year}"

        # Optional fields
        title = fields.get('TI', ['No Title'])[0]
        journal = fields.get('JT', ['Unknown Journal'])[0]
        doi = fields.get('LID', [''])[0].replace(' [doi]', '')
        url = f"https://doi.org/{doi}" if doi else ''
        volume = fields.get('VI', [''])[0]
        issue = fields.get('IP', [''])[0]
        pages = fields.get('PG', [''])[0]
        issn = fields.get('IS', [''])[0]
        month = 'may'  # You can customize this from DP if needed
        numpages = ''
        if pages and '–' in pages:
            start, end = pages.split('–', 1)
            try:
                numpages = str(int(end.strip()) - int(start.strip()) + 1)
            except:
                numpages = ''

        bib_entry = f"""@article{{{bibkey},
author       = {{{authors}}},
title        = {{{title}}},
year         = {{{year}}},
issue_date   = {{{fields.get('DP', [''])[0]}}},
publisher    = {{Oxford University Press, Inc.}},
address      = {{USA}},
volume       = {{{volume}}},
number       = {{{issue}}},
issn         = {{{issn}}},
url          = {{{url}}},
doi          = {{{doi}}},
journal      = {{{journal}}},
month        = {{{month}}},
pages        = {{{pages}}},
numpages     = {{{numpages}}}
}}"""
        bib_entries.append(bib_entry)

    return '\n\n'.join(bib_entries)


def nbib2bibtex(nbib, bib):
    """
    nbib2bibtex is 

    Arges:
        nbib: input file 
        bib: output file
    Exemple:
        nbib2bibtex(nbib, bib)
    """

    # 使用 glob 匹配所有符合条件的 nbib 文件
    nbib_files = glob.glob(nbib)
    
    if not nbib_files:
        print(f"Cannot find any file matching pattern: {nbib}")
        return
    
    # 创建输出目录（如果不存在）
    output_dir = os.path.dirname(bib)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # 处理每个 nbib 文件
    for nbib_file in nbib_files:
        print(f"Processing file: {nbib_file}")
        
        try:
            # 读取 nbib 文件内容
            with open(nbib_file, 'r', encoding='utf-8') as f:
                nbib_data = f.read()
            
            # 转换为 BibTeX 格式
            bib_output = parse_nbib_to_bibtex(nbib_data)
            
            if not bib_output.strip():
                print(f"❌ No valid entries found in file: {nbib_file}")
                continue
            
            # 追加到输出文件
            write_mode = 'a' if os.path.exists(bib) else 'w'
            
            with open(bib, write_mode, encoding='utf-8') as f:
                # 添加分隔换行（非首个条目）
                if write_mode == 'a' and f.tell() > 0:  # 检查文件是否非空
                    f.write('\n\n')
                f.write(bib_output)

        except FileNotFoundError:
            print(f"❌ File not found: {nbib}")