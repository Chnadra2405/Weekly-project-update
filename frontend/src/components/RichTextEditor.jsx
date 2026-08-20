import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Highlight from "@tiptap/extension-highlight";
import Typography from "@tiptap/extension-typography";
import { AutoCorrect } from "./AutoCorrectExtension";
import { Bold, Italic, List, Highlighter } from "lucide-react";
import { useEffect, useState } from "react";

const EMPTY_HTML = "<p></p>";

function ToolbarButton({ onClick, isActive, title, children }) {
  return (
    <button
      type="button"
      onMouseDown={(e) => { e.preventDefault(); onClick(); }}
      className={`ssg-rte__btn${isActive ? " is-active" : ""}`}
      title={title}
      aria-pressed={isActive}
    >
      {children}
    </button>
  );
}

const HIGHLIGHT_COLORS = [
  { name: "Yellow", color: "#FFFF00" },
  { name: "Green", color: "#90EE90" },
  { name: "Blue", color: "#ADD8E6" },
  { name: "Pink", color: "#FFB6C1" },
  { name: "Orange", color: "#FFB347" },
];

export default function RichTextEditor({ id, value, onChange, disabled, invalid, describedBy }) {
  const [highlightOpen, setHighlightOpen] = useState(false);
  const editor = useEditor({
    extensions: [
      StarterKit.configure({ orderedList: false }),
      Highlight.configure({ multicolor: true }),
      Typography,
      AutoCorrect,
    ],
    content: value || "",
    editable: !disabled,
    editorProps: {
      attributes: {
        role: "textbox",
        "aria-multiline": "true",
        spellcheck: "true",
        autocorrect: "on",
        autocapitalize: "sentences",
        ...(id ? { id } : {}),
        ...(invalid ? { "aria-invalid": "true" } : {}),
        ...(describedBy ? { "aria-describedby": describedBy } : {}),
      },
    },
    onUpdate({ editor: ed }) {
      const html = ed.getHTML();
      onChange(html === EMPTY_HTML ? "" : html);
    },
  });

  useEffect(() => {
    if (!editor) return;
    editor.setEditable(!disabled);
  }, [disabled, editor]);

  useEffect(() => {
    if (!editor || editor.isDestroyed) return;
    const current = editor.getHTML();
    const normalised = current === EMPTY_HTML ? "" : current;
    const incoming = value || "";
    if (normalised !== incoming) {
      editor.commands.setContent(incoming, false);
    }
  }, [value, editor]);

  return (
    <div className={`ssg-rte${invalid ? " ssg-rte--invalid" : ""}`}>
      <div className="ssg-rte__toolbar" role="toolbar" aria-label="Text formatting">
        <ToolbarButton
          onClick={() => editor?.chain().focus().toggleBold().run()}
          isActive={editor?.isActive("bold") ?? false}
          title="Bold"
        >
          <Bold size={14} aria-hidden="true" />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor?.chain().focus().toggleItalic().run()}
          isActive={editor?.isActive("italic") ?? false}
          title="Italic"
        >
          <Italic size={14} aria-hidden="true" />
        </ToolbarButton>
        <span className="ssg-rte__sep" role="separator" aria-orientation="vertical" />
        <ToolbarButton
          onClick={() => editor?.chain().focus().toggleBulletList().run()}
          isActive={editor?.isActive("bulletList") ?? false}
          title="Bullet list"
        >
          <List size={14} aria-hidden="true" />
        </ToolbarButton>
        <span className="ssg-rte__sep" role="separator" aria-orientation="vertical" />
        <div className="ssg-rte__highlight-menu">
          <button
            type="button"
            onMouseDown={(e) => { e.preventDefault(); setHighlightOpen(!highlightOpen); }}
            className={`ssg-rte__btn${editor?.isActive("highlight") ? " is-active" : ""}`}
            title="Text highlight"
            aria-pressed={editor?.isActive("highlight") ?? false}
            aria-haspopup="true"
            aria-expanded={highlightOpen}
          >
            <Highlighter size={14} aria-hidden="true" />
          </button>
          {highlightOpen && (
            <div className="ssg-rte__color-palette" role="menu">
              <button
                type="button"
                onMouseDown={(e) => {
                  e.preventDefault();
                  editor?.chain().focus().unsetHighlight().run();
                  setHighlightOpen(false);
                }}
                className="ssg-rte__color-btn ssg-rte__color-btn--clear"
                title="Clear highlight"
              >
                None
              </button>
              {HIGHLIGHT_COLORS.map((hl) => (
                <button
                  key={hl.color}
                  type="button"
                  onMouseDown={(e) => {
                    e.preventDefault();
                    editor?.chain().focus().setHighlight({ color: hl.color }).run();
                    setHighlightOpen(false);
                  }}
                  className="ssg-rte__color-btn"
                  style={{ backgroundColor: hl.color }}
                  title={`Highlight ${hl.name}`}
                  aria-label={`${hl.name} highlight`}
                />
              ))}
            </div>
          )}
        </div>
      </div>
      <EditorContent editor={editor} />
    </div>
  );
}
