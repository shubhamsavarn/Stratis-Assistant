import React from 'react'
import { ChatInterface } from './components/ChatInterface'
import { motion } from 'framer-motion'

function App() {
  return (
    <motion.div 
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="min-h-screen bg-[#08090a]"
    >
      <ChatInterface />
    </motion.div>
  )
}

export default App
