"""
Reddit loader for Discovery Engine.
Parses the DOCX containing 7 Reddit threads into structured records.
Produces one record per post and one per comment, grouping them via meta.thread_id.
"""

import docx
import re
import hashlib
from typing import Iterator, Dict, Any, List

def load_reddit(file_path: str = "data/input/reddit_threads.docx") -> Iterator[Dict[str, Any]]:
    """
    Yields normalized records from Reddit DOCX.
    Schema:
      - record_id: sha256 of "reddit:" + thread_id + ":" + type + ":" + index
      - source: "reddit"
      - text: text to classify (includes thread title context for comments)
      - created_at: relative timestamp string or None
      - meta: { thread_id, thread_title, record_type, author, subreddit, ... }
    """
    doc = docx.Document(file_path)
    tabs: List[tuple] = []
    current_tab = None
    current_lines: List[tuple] = []
    
    for p in doc.paragraphs:
        txt = p.text.strip()
        if p.style.name.lower().startswith("title") or (txt.startswith("Tab ") and len(txt) < 10):
            if current_tab:
                tabs.append((current_tab, current_lines))
            current_tab = txt
            current_lines = []
        else:
            if current_tab and txt:
                for line in txt.split("\n"):
                    l = line.strip()
                    if l:
                        current_lines.append((p.style.name, l))
    if current_tab:
        tabs.append((current_tab, current_lines))

    time_re = re.compile(r"^(?:OP)?•?\s*\d+\s*(?:mo|d|h|m|y|s|w)\s*ago$", re.I)

    for tab_idx, (tab_name, lines) in enumerate(tabs, 1):
        thread_id = f"tab_{tab_idx}"
        
        # Locate Heading 1
        h1_idx = -1
        for i, (style, l) in enumerate(lines):
            if style.lower().startswith("heading 1") or (h1_idx == -1 and ("scam" in l.lower() or ("myntra" in l.lower() and len(l) > 30))):
                h1_idx = i
                break
        if h1_idx == -1:
            h1_idx = 0
            
        thread_title = lines[h1_idx][1]
        
        # Header info before H1
        post_author = None
        post_time = None
        subreddit = "r/MyntraSucks"
        
        for i in range(h1_idx):
            l = lines[i][1]
            if l.startswith("r/"):
                subreddit = l
            elif time_re.search(l) or "ago" in l:
                post_time = l.replace("•", "").strip()
            elif l not in ["•"]:
                post_author = l
                
        # Lines after H1
        post_body_lines: List[str] = []
        comments: List[Dict[str, Any]] = []
        current_comment = None
        
        i = h1_idx + 1
        while i < len(lines):
            style, l = lines[i]
            is_time = bool(time_re.search(l))
            has_next_time = (i + 1 < len(lines) and bool(time_re.search(lines[i+1][1])))
            
            if has_next_time and len(l) < 50:
                if current_comment:
                    comments.append(current_comment)
                current_comment = {
                    "author": l.replace("Top 1% Commenter", "").strip(),
                    "created_at": lines[i+1][1].replace("•", "").replace("OP", "").strip(),
                    "lines": []
                }
                i += 2
                continue
            elif is_time and not current_comment and not post_body_lines:
                post_time = l.replace("•", "").strip()
                i += 1
                continue
            else:
                if current_comment:
                    if l != "Top 1% Commenter":
                        current_comment["lines"].append(l)
                else:
                    if l.startswith("r/"):
                        subreddit = l
                    elif l in ["Fuck Myntra 👺", "Are You Kidding me 😬", "Shamelessly Looting the Shoppers 😠"]:
                        post_body_lines.append(l)
                    else:
                        post_body_lines.append(l)
                i += 1
                
        if current_comment:
            comments.append(current_comment)
            
        # Post record
        post_text = f"{thread_title}\n\n" + "\n".join(post_body_lines) if post_body_lines else thread_title
        post_rec_id = hashlib.sha256(f"reddit:{thread_id}:post".encode("utf-8")).hexdigest()
        yield {
            "record_id": post_rec_id,
            "source": "reddit",
            "text": post_text.strip(),
            "created_at": post_time,
            "meta": {
                "thread_id": thread_id,
                "tab_name": tab_name,
                "thread_title": thread_title,
                "record_type": "post",
                "author": post_author,
                "subreddit": subreddit
            }
        }
        
        # Comment records
        for c_idx, c in enumerate(comments, 1):
            c_text = "\n".join(c["lines"]).strip()
            if not c_text:
                continue
            full_text = f"[Thread: {thread_title}] {c_text}"
            c_rec_id = hashlib.sha256(f"reddit:{thread_id}:comment:{c_idx}".encode("utf-8")).hexdigest()
            yield {
                "record_id": c_rec_id,
                "source": "reddit",
                "text": full_text,
                "created_at": c.get("created_at"),
                "meta": {
                    "thread_id": thread_id,
                    "tab_name": tab_name,
                    "thread_title": thread_title,
                    "record_type": "comment",
                    "comment_index": c_idx,
                    "author": c.get("author"),
                    "subreddit": subreddit,
                    "raw_comment_text": c_text
                }
            }
