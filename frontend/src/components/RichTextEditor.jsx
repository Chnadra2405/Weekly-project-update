import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import { Bold, Italic, List, ListOrdered } from "lucide-react";
import { useEffect } from "react";

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

export default function RichTextEditor({ id, value, onChange, disabled, invalid, describedBy }) {
  const editor = useEditor({
    extensions: [StarterKit],
    content: value || "",
    editable: !disabled,
    editorProps: {
      attributes: {
        role: "textbox",
        "aria-multiline": "true",
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
        <ToolbarButton
          onClick={() => editor?.chain().focus().toggleOrderedList().run()}
          isActive={editor?.isActive("orderedList") ?? false}
          title="Numbered list"
        >
          <ListOrdered size={14} aria-hidden="true" />
        </ToolbarButton>
      </div>
      <EditorContent editor={editor} />
    </div>
  );
}
