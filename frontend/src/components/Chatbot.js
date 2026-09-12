import React, { useState, useEffect, useRef } from 'react'
import { Button, Modal, Form, Spinner, Alert, Badge } from 'react-bootstrap'
import { useSelector } from 'react-redux'
import axios from 'axios'

const Chatbot = () => {
    const [show, setShow] = useState(false)
    const [messages, setMessages] = useState([])
    const [inputMessage, setInputMessage] = useState('')
    const [isLoading, setIsLoading] = useState(false)
    const [error, setError] = useState('')
    const [isTyping, setIsTyping] = useState(false)
    const [orderCreated, setOrderCreated] = useState(false)
    const [orderData, setOrderData] = useState(null)
    const [pendingOrder, setPendingOrder] = useState(null)
    const [needsAddress, setNeedsAddress] = useState(false)
    const messagesEndRef = useRef(null)
    
    // Get user info from Redux store
    const userLogin = useSelector(state => state.userLogin)
    const { userInfo } = userLogin

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
    }

    useEffect(() => {
        scrollToBottom()
    }, [messages])

    useEffect(() => {
        // Initialize with welcome message
        if (messages.length === 0) {
            const welcomeMessage = userInfo 
                ? `Hi ${userInfo.name}! I'm your Digital Edge shopping assistant. I can help you find products and even place orders directly through chat. How can I help you today?`
                : "Hi! I'm your Digital Edge shopping assistant. I can help you find products and answer questions. For ordering, please log in first. How can I help you today?";
            
            setMessages([{
                id: 1,
                text: welcomeMessage,
                sender: 'bot',
                timestamp: new Date()
            }])
        }
    }, [userInfo])

    const sendMessage = async (e) => {
        e.preventDefault()
        if (!inputMessage.trim() || isLoading) return

        const userMessage = {
            id: Date.now(),
            text: inputMessage,
            sender: 'user',
            timestamp: new Date()
        }

        setMessages(prev => [...prev, userMessage])
        setInputMessage('')
        setIsLoading(true)
        setError('')
        setIsTyping(true)

        try {
            const chatHistory = messages.map(msg => ({
                role: msg.sender === 'user' ? 'user' : 'assistant',
                content: msg.text
            }))

            // Choose endpoint based on authentication
            const endpoint = userInfo ? '/api/chatbot/chat/authenticated/' : '/api/chatbot/chat/'
            
            const response = await axios.post(endpoint, {
                message: inputMessage,
                chat_history: chatHistory,
                pending_order: pendingOrder
            }, {
                headers: userInfo ? {
                    'Authorization': `Bearer ${userInfo.token}`
                } : {}
            })

            const botMessage = {
                id: Date.now() + 1,
                text: response.data.response,
                sender: 'bot',
                timestamp: new Date(),
                orderCreated: response.data.order_created || false,
                orderData: response.data.order_data || null
            }

            // Handle order creation
            if (response.data.order_created) {
                setOrderCreated(true)
                setOrderData(response.data.order_data)
                setPendingOrder(null)
                setNeedsAddress(false)
            }
            
            // Handle pending order and address collection
            if (response.data.pending_order) {
                setPendingOrder(response.data.pending_order)
                setNeedsAddress(true)
            } else if (response.data.needs_address === false) {
                setPendingOrder(null)
                setNeedsAddress(false)
            }

            setTimeout(() => {
                setMessages(prev => [...prev, botMessage])
                setIsTyping(false)
                setIsLoading(false)
            }, 1000) // Simulate typing delay

        } catch (err) {
            console.error('Chatbot error:', err)
            setError('Sorry, I encountered an error. Please try again.')
            setIsTyping(false)
            setIsLoading(false)
        }
    }

    const clearChat = () => {
        setMessages([{
            id: 1,
            text: "Hi! I'm your Digital Edge shopping assistant. How can I help you find the perfect electronics today?",
            sender: 'bot',
            timestamp: new Date()
        }])
        setError('')
    }

    const formatTime = (timestamp) => {
        return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    return (
        <>
            {/* Floating Chat Button */}
            <Button
                variant="primary"
                className="chatbot-toggle-btn"
                onClick={() => setShow(true)}
                style={{
                    position: 'fixed',
                    bottom: '20px',
                    right: '20px',
                    width: '60px',
                    height: '60px',
                    borderRadius: '50%',
                    zIndex: 1000,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '24px'
                }}
            >
                <i className="fas fa-robot"></i>
            </Button>

            {/* Chat Modal */}
            <Modal
                show={show}
                onHide={() => setShow(false)}
                size="md"
                centered
                className="chatbot-modal"
            >
                <Modal.Header 
                    closeButton 
                    style={{ 
                        backgroundColor: '#007bff', 
                        color: 'white',
                        borderBottom: 'none'
                    }}
                >
                    <Modal.Title style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                        <i className="fas fa-robot"></i> Digital Edge Assistant
                        {userInfo && (
                            <Badge bg="success" style={{ fontSize: '12px' }}>
                                <i className="fas fa-user"></i> {userInfo.name}
                            </Badge>
                        )}
                        {!userInfo && (
                            <Badge bg="warning" style={{ fontSize: '12px' }}>
                                <i className="fas fa-lock"></i> Guest
                            </Badge>
                        )}
                    </Modal.Title>
                </Modal.Header>
                
                <Modal.Body 
                    style={{ 
                        padding: '0',
                        height: '400px',
                        display: 'flex',
                        flexDirection: 'column'
                    }}
                >
                    {/* Messages Container */}
                    <div 
                        style={{ 
                            flex: 1,
                            overflowY: 'auto',
                            padding: '15px',
                            backgroundColor: '#f8f9fa'
                        }}
                    >
                        {messages.map((message) => (
                            <div
                                key={message.id}
                                style={{
                                    display: 'flex',
                                    justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                                    marginBottom: '15px'
                                }}
                            >
                                <div
                                    style={{
                                        maxWidth: '70%',
                                        padding: '10px 15px',
                                        borderRadius: '18px',
                                        backgroundColor: message.sender === 'user' ? '#007bff' : '#e9ecef',
                                        color: message.sender === 'user' ? 'white' : 'black',
                                        position: 'relative'
                                    }}
                                >
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '5px' }}>
                                        <i className={`fas ${message.sender === 'bot' ? 'fa-robot' : 'fa-user'}`} style={{ fontSize: '12px' }}></i>
                                        <small style={{ opacity: 0.7 }}>
                                            {formatTime(message.timestamp)}
                                        </small>
                                    </div>
                                    <div style={{ whiteSpace: 'pre-wrap' }}>
                                        {message.text}
                                    </div>
                                    
                                    {/* Show order information if order was created */}
                                    {message.orderCreated && message.orderData && (
                                        <div style={{
                                            marginTop: '10px',
                                            padding: '10px',
                                            backgroundColor: '#d4edda',
                                            border: '1px solid #c3e6cb',
                                            borderRadius: '5px',
                                            fontSize: '14px'
                                        }}>
                                            <strong>🎉 Order Created Successfully!</strong>
                                            <br />
                                            <strong>Order ID:</strong> #{message.orderData.order_id}
                                            <br />
                                            <strong>Total:</strong> ${message.orderData.order.total.toFixed(2)}
                                            <br />
                                            <strong>Status:</strong> {message.orderData.order.status}
                                            <br />
                                            <strong>Items:</strong>
                                            {message.orderData.order.items.map((item, idx) => (
                                                <div key={idx} style={{ marginLeft: '10px' }}>
                                                    • {item.name} (Qty: {item.quantity}) - ${item.price.toFixed(2)}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                        
                        {isTyping && (
                            <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '15px' }}>
                                <div style={{
                                    padding: '10px 15px',
                                    borderRadius: '18px',
                                    backgroundColor: '#e9ecef',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '5px'
                                }}>
                                    <i className="fas fa-robot" style={{ fontSize: '12px' }}></i>
                                    <Spinner animation="border" size="sm" />
                                    <span style={{ marginLeft: '5px' }}>Typing...</span>
                                </div>
                            </div>
                        )}
                        
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Error Message */}
                    {error && (
                        <Alert variant="danger" style={{ margin: '10px', marginBottom: '0' }}>
                            {error}
                        </Alert>
                    )}

                    {/* Input Form */}
                    <Form onSubmit={sendMessage} style={{ padding: '15px', borderTop: '1px solid #dee2e6' }}>
                        {!userInfo && (
                            <Alert variant="info" style={{ marginBottom: '10px', fontSize: '14px' }}>
                                <i className="fas fa-info-circle"></i> 
                                <strong> Guest Mode:</strong> You can browse products and ask questions. 
                                <a href="/login" style={{ color: '#0c5460', textDecoration: 'underline' }}> Login</a> to place orders directly through chat!
                            </Alert>
                        )}
                        
                        {pendingOrder && (
                            <Alert variant="warning" style={{ marginBottom: '10px', fontSize: '14px' }}>
                                <i className="fas fa-shopping-cart"></i> 
                                <strong> Order in Progress:</strong> 
                                {pendingOrder.waiting_for_selection && " Please select a product from the options above."}
                                {pendingOrder.waiting_for_confirmation && ` Please confirm your order for ${pendingOrder.product.name} (Qty: ${pendingOrder.quantity})`}
                                {needsAddress && !pendingOrder.waiting_for_confirmation && !pendingOrder.waiting_for_selection && ` Please provide your shipping address to complete your order for ${pendingOrder.product.name} (Qty: ${pendingOrder.quantity})`}
                            </Alert>
                        )}
                        
                        <div style={{ display: 'flex', gap: '10px' }}>
                            <Form.Control
                                type="text"
                                placeholder={
                                    pendingOrder?.waiting_for_selection
                                        ? "Select a product (e.g., 'I want the first one' or 'I want Samsung Galaxy S23 Ultra')..."
                                        : pendingOrder?.waiting_for_confirmation
                                        ? "Confirm your order (e.g., 'Yes' or 'Confirm')..."
                                        : needsAddress 
                                        ? "Provide your shipping address (address, city, postal code, country)..." 
                                        : userInfo 
                                        ? "Type your message or order request..." 
                                        : "Type your message..."
                                }
                                value={inputMessage}
                                onChange={(e) => setInputMessage(e.target.value)}
                                disabled={isLoading}
                                style={{ borderRadius: '20px' }}
                            />
                            <Button
                                type="submit"
                                variant="primary"
                                disabled={!inputMessage.trim() || isLoading}
                                style={{ borderRadius: '50%', width: '40px', height: '40px' }}
                            >
                                <i className="fas fa-paper-plane"></i>
                            </Button>
                        </div>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px' }}>
                            <Button
                                variant="outline-secondary"
                                size="sm"
                                onClick={clearChat}
                            >
                                Clear Chat
                            </Button>
                            <small className="text-muted">
                                Powered by AI Assistant
                            </small>
                        </div>
                    </Form>
                </Modal.Body>
            </Modal>

            {/* Custom CSS */}
            <style jsx>{`
                .chatbot-toggle-btn:hover {
                    transform: scale(1.1);
                    transition: transform 0.2s ease;
                }
                
                .chatbot-modal .modal-content {
                    border-radius: 15px;
                    overflow: hidden;
                }
                
                .chatbot-modal .modal-header {
                    border-radius: 15px 15px 0 0;
                }
            `}</style>
        </>
    )
}

export default Chatbot
