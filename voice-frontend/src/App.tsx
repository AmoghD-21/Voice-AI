// import React, { useState, useRef } from 'react';
// export default function App() {
//   const [isConnected, setIsConnected] = useState<boolean>(false);
//   const [status, setStatus] = useState<string>('Disconnected');
//   const [isTalking, setIsTalking] = useState<boolean>(false);
  
//   const wsRef = useRef<WebSocket | null>(null);
//   const audioContextRef = useRef<AudioContext | null>(null);
//   const mediaStreamRef = useRef<MediaStream | null>(null);
//   const processorRef = useRef<ScriptProcessorNode | null>(null);

//   // 1. Establish connection to our FastAPI Backend
//   // const startConversation = async () => {
//   //   try {
//   //     setStatus('Connecting to voice server...');
      
//   //     // Request microphone access from the user
//   //     const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//   //     mediaStreamRef.current = stream;

//   //     // Establish live WebSocket connection
//   //     const socket = new WebSocket('ws://localhost:8000/ws');
//   //     wsRef.current = socket;

//   //     socket.onopen = () => {
//   //       setIsConnected(true);
//   //       setStatus('Connected & Listening 🎙️');
//   //       initializeAudioPipeline(stream);
//   //     };

//   //     // 2. Handle audio packets coming from the Backend
//   //     socket.onmessage = async (event) => {
//   //       setIsTalking(true);
//   //       // Play the incoming audio chunk
//   //       if (event.data instanceof Blob) {
//   //         const arrayBuffer = await event.data.arrayBuffer();
//   //         playAudioChunk(arrayBuffer);
//   //       }
//   //       setTimeout(() => setIsTalking(false), 800);
//   //     };

//   //     socket.onclose = () => {
//   //       stopConversation();
//   //     };

//   //     socket.onerror = (error) => {
//   //       console.error("WebSocket Error:", error);
//   //       setStatus('Connection error occurred.');
//   //     };

//   //   } catch (err) {
//   //     console.error("Failed to access mic or server:", err);
//   //     setStatus('Microphone access denied or server offline.');
//   //   }
//   // };

  
// const startConversation = async () => {
//     try {
//       setStatus('Connecting to voice server...');
      
//       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//       mediaStreamRef.current = stream;

//       const socket = new WebSocket('ws://localhost:8000/ws');
//       wsRef.current = socket;

//       socket.onopen = () => {
//         setIsConnected(true);
//         setStatus('Connected & Listening 🎙️');
        
//         // Use MediaRecorder for more stable cross-browser streaming chunks
//         const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
        
//         mediaRecorder.ondataavailable = (event) => {
//           if (event.data.size > 0 && socket.readyState === WebSocket.OPEN) {
//             socket.send(event.data);
//           }
//         };
        
//         // Send small, continuous audio slices every 100ms
//         mediaRecorder.start(100);
//       };

//       socket.onmessage = async (event) => {
//         setIsTalking(true);
//         if (event.data instanceof Blob) {
//           const arrayBuffer = await event.data.arrayBuffer();
//           playAudioChunk(arrayBuffer);
//         }
//         setTimeout(() => setIsTalking(false), 800);
//       };

//       socket.onclose = () => { stopConversation(); };
//       socket.onerror = () => { setStatus('Connection error.'); };

//     } catch (err) {
//       setStatus('Microphone access denied or server offline.');
//     }
//   };


//   // 3. Capture audio from mic and stream chunks to Backend
//   // const initializeAudioPipeline = (stream: MediaStream) => {
//   //   const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
//   //   audioContextRef.current = audioContext;

//   //   const source = audioContext.createMediaStreamSource(stream);
    
//   //   // Create a processor to intercept microphone PCM raw chunks
//   //   const processor = audioContext.createScriptProcessor(4096, 1, 1);
//   //   processorRef.current = processor;

//   //   processor.onaudioprocess = (e) => {
//   //     if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
//   //       const inputData = e.inputBuffer.getChannelData(0);
//   //       // Convert floating point audio to 16-bit Int Array (PCM)
//   //       const pcmBuffer = Float32ToInt16(inputData);
//   //       wsRef.current.send(pcmBuffer);
//   //     }
//   //   };

//   //   source.connect(processor);
//   //   processor.connect(audioContext.destination);
//   // };

//   // Helper function to play raw audio frames natively in browser
//   const playAudioChunk = async (arrayBuffer: ArrayBuffer) => {
//     if (!audioContextRef.current) return;
//     try {
//       // Decode raw bytes to sound buffer
//       const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
//       const source = audioContextRef.current.createBufferSource();
//       source.buffer = audioBuffer;
//       source.connect(audioContextRef.current.destination);
//       source.start(0);
//     } catch (e) {
//       // Audio framing catch-all
//     }
//   };

//   // Convert floats to browser-compatible Int16 array
//   // const Float32ToInt16 = (buffer: Float32Array) => {
//   //   let l = buffer.length;
//   //   let buf = new Int16Array(l);
//   //   while (l--) {
//   //     buf[l] = Math.min(1, buffer[l]) * 0x7FFF;
//   //   }
//   //   return buf.buffer;
//   // };

//   const stopConversation = () => {
//     setStatus('Disconnected');
//     setIsConnected(false);
//     setIsTalking(false);

//     if (wsRef.current) wsRef.current.close();
//     if (processorRef.current) processorRef.current.disconnect();
//     if (audioContextRef.current) audioContextRef.current.close();
//     if (mediaStreamRef.current) {
//       mediaStreamRef.current.getTracks().forEach(track => track.stop());
//     }
//   };

//   return (
//     <div style={styles.container}>
//       <h1 style={styles.title}>Real-Time Voice AI Agent</h1>
//       <p style={styles.subtitle}>Powered by Pipecat, FastAPI, & Local RAG Vector Store</p>
      
//       <div style={{...styles.statusWidget, backgroundColor: isConnected ? '#e6f4ea' : '#f1f3f4'}}>
//         <div style={{...styles.pulseDot, backgroundColor: isConnected ? '#137333' : '#5f6368'}} className={isConnected ? 'pulse' : ''} />
//         <span style={styles.statusText}>{status}</span>
//       </div>

//       {isTalking && <div style={styles.talkingIndicator}>AI is speaking... 🔊</div>}

//       <div style={styles.buttonContainer}>
//         {!isConnected ? (
//           <button onClick={startConversation} style={styles.startButton}>
//             Start Live Voice Chat
//           </button>
//         ) : (
//           <button onClick={stopConversation} style={styles.stopButton}>
//             Disconnect Call
//           </button>
//         )}
//       </div>
//     </div>
//   );
// }

// // Minimalistic UI Styling object
// const styles: { [key: string]: React.CSSProperties } = {
//   container: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', fontFamily: 'Segoe UI, Tahoma, Geneva, Verdana, sans-serif', backgroundColor: '#fafafa', color: '#333' },
//   title: { fontSize: '2.5rem', marginBottom: '0.5rem', fontWeight: 600 },
//   subtitle: { color: '#666', marginBottom: '2rem' },
//   statusWidget: { display: 'flex', alignItems: 'center', padding: '0.75rem 1.5rem', borderRadius: '30px', boxShadow: '0 2px 5px rgba(0,0,0,0.05)', marginBottom: '2rem' },
//   pulseDot: { width: '12px', height: '12px', borderRadius: '50%', marginRight: '10px' },
//   statusText: { fontSize: '1rem', fontWeight: '500' },
//   buttonContainer: { marginTop: '1rem' },
//   startButton: { padding: '1rem 2.5rem', fontSize: '1.2rem', color: '#fff', backgroundColor: '#1a73e8', border: 'none', borderRadius: '8px', cursor: 'pointer', transition: 'background-color 0.2s', fontWeight: 'bold', boxShadow: '0 4px 6px rgba(26,115,232,0.2)' },
//   stopButton: { padding: '1rem 2.5rem', fontSize: '1.2rem', color: '#fff', backgroundColor: '#d93025', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', boxShadow: '0 4px 6px rgba(217,48,37,0.2)' },
//   talkingIndicator: { color: '#1a73e8', fontWeight: 'bold', animation: 'blink 1s infinite', marginBottom: '1rem' }
// };



import React, { useState, useRef } from 'react';

export default function App() {
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [status, setStatus] = useState<string>('Disconnected');
  const [isTalking, setIsTalking] = useState<boolean>(false);
  
  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);

  const startConversation = async () => {
    try {
      setStatus('Connecting to voice server...');
      
      // 1. Get user microphone access
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      // 2. Open our working FastAPI WebSocket
      const socket = new WebSocket('ws://localhost:8000/ws');
      wsRef.current = socket;

      socket.onopen = () => {
        setIsConnected(true);
        setStatus('Connected & Listening 🎙️');
        initializePCMStream(stream);
      };

      // 3. Play incoming voice data chunks
      socket.onmessage = async (event) => {
        setIsTalking(true);
        if (event.data instanceof Blob) {
          const arrayBuffer = await event.data.arrayBuffer();
          playAudioChunk(arrayBuffer);
        }
        setTimeout(() => setIsTalking(false), 1200);
      };

      socket.onclose = () => { stopConversation(); };
      socket.onerror = () => { setStatus('Connection error occurred.'); };

    } catch (err) {
      console.error(err);
      setStatus('Microphone access denied or server offline.');
    }
  };

  // 4. Force browser to downsample and output RAW 16-bit PCM Audio Frames
  const initializePCMStream = (stream: MediaStream) => {
    // Pipecat expects a clean 16000Hz or 48000Hz frequency match
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({ sampleRate: 16000 });
    audioContextRef.current = audioContext;

    const source = audioContext.createMediaStreamSource(stream);
    const processor = audioContext.createScriptProcessor(2048, 1, 1);
    processorRef.current = processor;

    processor.onaudioprocess = (e) => {
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        const inputData = e.inputBuffer.getChannelData(0);
        
        // Convert the 32-bit floating point browser audio to standard 16-bit PCM Signed integers
        const buffer = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          buffer[i] = Math.max(-32768, Math.min(32767, inputData[i] * 32768));
        }
        
        // Stream the raw PCM array over the socket connection
        wsRef.current.send(buffer.buffer);
      }
    };

    source.connect(processor);
    processor.connect(audioContext.destination);
  };

  const playAudioChunk = async (arrayBuffer: ArrayBuffer) => {
    if (!audioContextRef.current) return;
    try {
      const audioBuffer = await audioContextRef.current.decodeAudioData(arrayBuffer);
      const source = audioContextRef.current.createBufferSource();
      source.buffer = audioBuffer;
      source.connect(audioContextRef.current.destination);
      source.start(0);
    } catch (e) {
      // Audio playback catch-all
    }
  };

  const stopConversation = () => {
    setStatus('Disconnected');
    setIsConnected(false);
    setIsTalking(false);
    if (wsRef.current) wsRef.current.close();
    if (processorRef.current) processorRef.current.disconnect();
    if (audioContextRef.current) audioContextRef.current.close();
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Real-Time Voice AI Agent</h1>
      <p style={styles.subtitle}>Powered by Pipecat, FastAPI, & Local RAG Vector Store</p>
      
      <div style={{...styles.statusWidget, backgroundColor: isConnected ? '#e6f4ea' : '#f1f3f4'}}>
        <span style={styles.statusText}>{status}</span>
      </div>

      {isTalking && <div style={styles.talkingIndicator}>AI is speaking... 🔊</div>}

      <div style={styles.buttonContainer}>
        {!isConnected ? (
          <button onClick={startConversation} style={styles.startButton}>Start Live Voice Chat</button>
        ) : (
          <button onClick={stopConversation} style={styles.stopButton}>Disconnect Call</button>
        )}
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: { display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', fontFamily: 'sans-serif', backgroundColor: '#fafafa', color: '#333' },
  title: { fontSize: '2.5rem', marginBottom: '0.5rem', fontWeight: 600 },
  subtitle: { color: '#666', marginBottom: '2rem' },
  statusWidget: { display: 'flex', alignItems: 'center', padding: '0.75rem 1.5rem', borderRadius: '30px', marginBottom: '2rem' },
  statusText: { fontSize: '1rem', fontWeight: '500' },
  buttonContainer: { marginTop: '1rem' },
  startButton: { padding: '1rem 2.5rem', fontSize: '1.2rem', color: '#fff', backgroundColor: '#1a73e8', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' },
  stopButton: { padding: '1rem 2.5rem', fontSize: '1.2rem', color: '#fff', backgroundColor: '#d93025', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' },
  talkingIndicator: { color: '#1a73e8', fontWeight: 'bold', marginBottom: '1rem' }
};