import { useEffect, useRef, useState } from "react"

const API = import.meta.env.VITE_API_URL || "http://localhost:8000"

type Msg = {role:"user"|"assistant", content:string, agent?:string}
type Doc = {id:string, filename:string, size:number, pages:number}

export default function App(){
  const [messages,setMessages]=useState<Msg[]>([])
  const [input,setInput]=useState("")
  const [docs,setDocs]=useState<Doc[]>([])
  const [selected,setSelected]=useState<string[]>([])
  const [agent,setAgent]=useState("orchestrator")
  const [loading,setLoading]=useState(false)
  const [image,setImage]=useState<string|undefined>()
  const [dark,setDark]=useState(true)
  const fileRef=useRef<HTMLInputElement>(null)

  async function refreshDocs(){
    const r=await fetch(`${API}/api/documents`); if(r.ok) setDocs(await r.json())
  }
  useEffect(()=>{refreshDocs()},[])

  async function upload(file:File){
    const fd=new FormData(); fd.append("file",file)
    const r=await fetch(`${API}/api/upload`,{method:"POST",body:fd})
    if(r.ok){ const d=await r.json(); setDocs(x=>[...x,d]); setSelected(x=>[...x,d.id]) }
  }

  async function send(){
    if(!input.trim() || loading) return
    const q=input.trim(); setInput(""); setMessages(m=>[...m,{role:"user",content:q}]); setLoading(true)
    try{
      const r=await fetch(`${API}/api/chat`,{method:"POST",headers:{"Content-Type":"application/json"},
        body:JSON.stringify({message:q,document_ids:selected,image_data_url:image})})
      const data=await r.json()
      setMessages(m=>[...m,{role:"assistant",content:data.answer,agent:data.agent}])
      setAgent(data.agent); setImage(undefined)
    }catch{setMessages(m=>[...m,{role:"assistant",content:"Backend is unreachable. Start FastAPI on port 8000."}])}
    finally{setLoading(false)}
  }

  function pickImage(e:React.ChangeEvent<HTMLInputElement>){
    const f=e.target.files?.[0]; if(!f) return
    const reader=new FileReader(); reader.onload=()=>setImage(String(reader.result)); reader.readAsDataURL(f)
  }

  return <div className={dark?"app dark":"app"}>
    <aside className="sidebar">
      <div className="brand"><div className="logo">K</div><div><b>Keval AI</b><span>Multi-Agent Workspace</span></div></div>
      <button className="new" onClick={()=>setMessages([])}>＋ New conversation</button>
      <div className="sideTitle">Agents</div>
      {["orchestrator","support","document","vision","research"].map(a=><div className={agent===a?"agent active":"agent"} key={a} onClick={()=>setAgent(a)}><span>●</span>{a[0].toUpperCase()+a.slice(1)} Agent</div>)}
      <div className="sideTitle">Documents</div>
      {docs.length===0?<small>No documents uploaded</small>:docs.map(d=><label className="doc" key={d.id}><input type="checkbox" checked={selected.includes(d.id)} onChange={()=>setSelected(s=>s.includes(d.id)?s.filter(x=>x!==d.id):[...s,d.id])}/>{d.filename}</label>)}
      <div className="grow"/>
      <button className="theme" onClick={()=>setDark(!dark)}>{dark?"☀ Light mode":"◐ Dark mode"}</button>
    </aside>
    <main className="main">
      <header><div><h1>AI Workspace</h1><p>Support, documents, vision and intelligent routing in one place.</p></div><div className="status"><i/> {agent} active</div></header>
      <section className="chat">
        {messages.length===0?<div className="welcome"><div className="heroIcon">✦</div><h2>How can I help?</h2><p>Ask a question, upload a document, or attach an image.</p><div className="chips">{["Summarize my PDF","Explain this document","Analyze an image","Customer support"].map(x=><button onClick={()=>setInput(x)} key={x}>{x}</button>)}</div></div>:messages.map((m,i)=><div className={m.role==="user"?"bubble user":"bubble"} key={i}><div className="role">{m.role==="user"?"You":`${m.agent||"AI"} agent`}</div><div className="content">{m.content}</div></div>)}
        {loading&&<div className="bubble"><div className="role">AI</div><div className="typing">Thinking…</div></div>}
      </section>
      <div className="composer">
        {image&&<div className="preview"><img src={image}/><button onClick={()=>setImage(undefined)}>×</button></div>}
        <div className="inputRow">
          <input value={input} onChange={e=>setInput(e.target.value)} onKeyDown={e=>{if(e.key==="Enter")send()}} placeholder="Message your AI workspace…"/>
          <input ref={fileRef} type="file" accept="image/*" hidden onChange={pickImage}/>
          <button className="attach" onClick={()=>fileRef.current?.click()}>＋</button>
          <button className="send" onClick={send}>↑</button>
        </div>
        <div className="hint">AI can make mistakes. Verify important information.</div>
      </div>
    </main>
  </div>
}
