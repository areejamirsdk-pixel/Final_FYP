import React, { useState, useEffect } from 'react'
import { Button, Row, Col, ListGroup, Image, Card, Modal } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import Message from '../components/Message'
import CheckoutSteps from '../components/CheckoutSteps'
import { createOrder } from '../actions/orderActions'
import { ORDER_CREATE_RESET } from '../constants/orderConstants'

function PlaceOrderScreen({ history }) {

    const orderCreate = useSelector(state => state.orderCreate)
    const { order, error, success } = orderCreate

    const dispatch = useDispatch()
    const [showModal, setShowModal] = useState(false)
    const [confirmedOrderId, setConfirmedOrderId] = useState(null)

    const cart = useSelector(state => state.cart)

    cart.itemsPrice = cart.cartItems.reduce((acc, item) => acc + item.price * item.qty, 0).toFixed(2)
    cart.shippingPrice = (cart.itemsPrice > 100 ? 0 : 2).toFixed(2)
    cart.taxPrice = Math.round(Number((0.082) * cart.itemsPrice)).toFixed(2)
    cart.totalPrice = (Number(cart.itemsPrice) + Number(cart.shippingPrice) + Number(cart.taxPrice)).toFixed(2)

    if (!cart.paymentMethod) {
        history.push('/payment')
    }

    useEffect(() => {
        if (success) {
            setConfirmedOrderId(order._id)
            setShowModal(true)
            dispatch({ type: ORDER_CREATE_RESET })
        }
    }, [success, history])

    const placeOrder = () => {
        dispatch(createOrder({
            orderItems: cart.cartItems,
            shippingAddress: cart.shippingAddress,
            paymentMethod: cart.paymentMethod,
            itemsPrice: cart.itemsPrice,
            shippingPrice: cart.shippingPrice,
            taxPrice: cart.taxPrice,
            totalPrice: cart.totalPrice,
        }))
    }

    const handleViewOrder = () => {
        setShowModal(false)
        history.push(`/order/${confirmedOrderId}`, { newOrder: true })
    }

    const handleContinueShopping = () => {
        setShowModal(false)
        history.push('/')
    }

    return (
        <div>
            {/* Order Confirmed Popup */}
            <Modal
                show={showModal}
                onHide={handleContinueShopping}
                centered
                backdrop="static"
            >
                <Modal.Body style={{ textAlign: 'center', padding: '40px 30px' }}>
                    {/* Checkmark circle */}
                    <div style={{
                        width: '80px',
                        height: '80px',
                        borderRadius: '50%',
                        background: 'linear-gradient(135deg, #28a745, #20c997)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        margin: '0 auto 20px auto',
                        boxShadow: '0 4px 15px rgba(40, 167, 69, 0.4)'
                    }}>
                        <span style={{ color: 'white', fontSize: '40px', lineHeight: 1 }}>✓</span>
                    </div>

                    <h3 style={{ fontWeight: '700', color: '#1a1a2e', marginBottom: '8px' }}>
                        Order Confirmed!
                    </h3>

                    <p style={{ color: '#6c757d', fontSize: '15px', marginBottom: '6px' }}>
                        Your order has been placed successfully.
                    </p>

                    {confirmedOrderId && (
                        <p style={{ color: '#495057', fontSize: '14px', marginBottom: '24px' }}>
                            Order ID: <strong>#{confirmedOrderId}</strong>
                        </p>
                    )}

                    <p style={{ color: '#6c757d', fontSize: '13px', marginBottom: '28px' }}>
                        A confirmation email has been sent to your registered email address.
                    </p>

                    <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
                        <Button
                            variant="outline-secondary"
                            onClick={handleViewOrder}
                            style={{
                                minWidth: '130px',
                                borderRadius: '25px',
                                fontWeight: '600',
                                fontSize: '14px'
                            }}
                        >
                            View Order
                        </Button>

                        <Button
                            variant="success"
                            onClick={handleContinueShopping}
                            style={{
                                minWidth: '160px',
                                borderRadius: '25px',
                                fontWeight: '600',
                                fontSize: '14px',
                                background: 'linear-gradient(135deg, #28a745, #20c997)',
                                border: 'none',
                                boxShadow: '0 4px 12px rgba(40, 167, 69, 0.3)'
                            }}
                        >
                            Continue Shopping
                        </Button>
                    </div>
                </Modal.Body>
            </Modal>

            <CheckoutSteps step1 step2 step3 step4 />
            <Row>
                <Col md={8}>
                    <ListGroup variant='flush'>
                        <ListGroup.Item>
                            <h2>Shipping</h2>
                            <p>
                                <strong>Shipping: </strong>
                                {cart.shippingAddress.address},  {cart.shippingAddress.city}
                                {'  '}
                                {cart.shippingAddress.postalCode},
                                {'  '}
                                {cart.shippingAddress.country}
                            </p>
                        </ListGroup.Item>

                        <ListGroup.Item>
                            <h2>Payment Method</h2>
                            <p>
                                <strong>Method: </strong>
                                {cart.paymentMethod}
                            </p>
                        </ListGroup.Item>

                        <ListGroup.Item>
                            <h2>Order Items</h2>
                            {cart.cartItems.length === 0 ? <Message variant='info'>
                                Your cart is empty
                            </Message> : (
                                <ListGroup variant='flush'>
                                    {cart.cartItems.map((item, index) => (
                                        <ListGroup.Item key={index}>
                                            <Row>
                                                <Col md={1}>
                                                    <Image src={item.image} alt={item.name} fluid rounded />
                                                </Col>
                                                <Col>
                                                    <Link to={`/product/${item.product}`}>{item.name}</Link>
                                                </Col>
                                                <Col md={4}>
                                                    {item.qty} X $ {item.price} = $ {(item.qty * item.price).toFixed(2)}
                                                </Col>
                                            </Row>
                                        </ListGroup.Item>
                                    ))}
                                </ListGroup>
                            )}
                        </ListGroup.Item>
                    </ListGroup>
                </Col>

                <Col md={4}>
                    <Card>
                        <ListGroup variant='flush'>
                            <ListGroup.Item>
                                <h2>Order Summary</h2>
                            </ListGroup.Item>

                            <ListGroup.Item>
                                <Row>
                                    <Col>Items:</Col>
                                    <Col>$ {cart.itemsPrice}</Col>
                                </Row>
                            </ListGroup.Item>

                            <ListGroup.Item>
                                <Row>
                                    <Col>Shipping:</Col>
                                    <Col>$ {cart.shippingPrice}</Col>
                                </Row>
                            </ListGroup.Item>

                            <ListGroup.Item>
                                <Row>
                                    <Col>Tax:</Col>
                                    <Col>$ {cart.taxPrice}</Col>
                                </Row>
                            </ListGroup.Item>

                            <ListGroup.Item>
                                <Row>
                                    <Col>Total:</Col>
                                    <Col>$ {cart.totalPrice}</Col>
                                </Row>
                            </ListGroup.Item>

                            <ListGroup.Item>
                                {error && <Message variant='danger'>{error}</Message>}
                            </ListGroup.Item>

                            <ListGroup.Item>
                                <Button
                                    type='button'
                                    className='btn-block'
                                    disabled={cart.cartItems === 0}
                                    onClick={placeOrder}
                                >
                                    Place Order
                                </Button>
                            </ListGroup.Item>
                        </ListGroup>
                    </Card>
                </Col>
            </Row>
        </div>
    )
}

export default PlaceOrderScreen
