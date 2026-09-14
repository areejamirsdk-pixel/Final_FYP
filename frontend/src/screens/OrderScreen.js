import React, { useState, useEffect } from 'react'
import { Button, Row, Col, ListGroup, Image, Card, Modal, Form } from 'react-bootstrap'
import { Link } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import { PayPalButton } from 'react-paypal-button-v2'
import Message from '../components/Message'
import Loader from '../components/Loader'
import { getOrderDetails, payOrder, deliverOrder } from '../actions/orderActions'
import { ORDER_PAY_RESET, ORDER_DELIVER_RESET } from '../constants/orderConstants'

function OrderScreen({ match, history }) {
    const orderId = match.params.id
    const dispatch = useDispatch()


    const [sdkReady, setSdkReady] = useState(false)
    const [showPaidModal, setShowPaidModal] = useState(false)
    const [cardNumber, setCardNumber] = useState('')
    const [cardName, setCardName] = useState('')
    const [cardExpiry, setCardExpiry] = useState('')
    const [cardCvv, setCardCvv] = useState('')
    const [cardError, setCardError] = useState('')

    const orderDetails = useSelector(state => state.orderDetails)
    const { order, error, loading } = orderDetails

    const orderPay = useSelector(state => state.orderPay)
    const { loading: loadingPay, success: successPay } = orderPay

    const orderDeliver = useSelector(state => state.orderDeliver)
    const { loading: loadingDeliver, success: successDeliver } = orderDeliver

    const userLogin = useSelector(state => state.userLogin)
    const { userInfo } = userLogin


    if (!loading && !error) {
        order.itemsPrice = order.orderItems.reduce((acc, item) => acc + item.price * item.qty, 0).toFixed(2)
    }


    const addPayPalScript = () => {
        const script = document.createElement('script')
        script.type = 'text/javascript'
        script.src = 'https://www.paypal.com/sdk/js?client-id=sb&currency=USD'
        // AeDXja18CkwFUkL-HQPySbzZsiTrN52cG13mf9Yz7KiV2vNnGfTDP0wDEN9sGlhZHrbb_USawcJzVDgn'
        script.async = true
        script.onload = () => {
            setSdkReady(true)
        }
        document.body.appendChild(script)
    }

    useEffect(() => {

        if (!userInfo) {
            history.push('/login')
        }

        if (!order || successPay || order._id !== Number(orderId) || successDeliver) {
            dispatch({ type: ORDER_PAY_RESET })
            dispatch({ type: ORDER_DELIVER_RESET })

            dispatch(getOrderDetails(orderId))
        } else if (!order.isPaid) {
            if (!window.paypal) {
                addPayPalScript()
            } else {
                setSdkReady(true)
            }
        }
    }, [dispatch, order, orderId, successPay, successDeliver])


    const successPaymentHandler = (paymentResult) => {
        dispatch(payOrder(orderId, paymentResult))
    }

    const cardPaymentHandler = (e) => {
        e.preventDefault()
        setCardError('')

        const digitsOnly = cardNumber.replace(/\s/g, '')
        if (digitsOnly.length < 13 || digitsOnly.length > 19 || !/^\d+$/.test(digitsOnly)) {
            setCardError('Please enter a valid card number.')
            return
        }
        if (!cardName.trim()) {
            setCardError('Please enter the name on the card.')
            return
        }
        if (!/^\d{2}\/\d{2}$/.test(cardExpiry)) {
            setCardError('Please enter expiry as MM/YY.')
            return
        }
        if (!/^\d{3,4}$/.test(cardCvv)) {
            setCardError('Please enter a valid CVV.')
            return
        }

        dispatch(payOrder(orderId, {
            id: 'CARD-' + Date.now(),
            status: 'COMPLETED',
            update_time: new Date().toISOString(),
            payer: { email_address: userInfo ? userInfo.email : '' },
        }))
    }

    useEffect(() => {
        if (successPay) {
            setShowPaidModal(true)
        }
    }, [successPay])

    useEffect(() => {
        if (!loading && !error && order && order.paymentMethod === 'COD') {
            setShowPaidModal(true)
        }
    }, [loading, error, order])

    const handleContinueShopping = () => {
        setShowPaidModal(false)
        history.push('/')
    }

    const deliverHandler = () => {
        dispatch(deliverOrder(order))
    }

    return loading ? (
        <Loader />
    ) : error ? (
        <Message variant='danger'>{error}</Message>
    ) : (
                <div>
                    <h1>Order: {order.Id}</h1>
                    <Row>
                        <Col md={8}>
                            <ListGroup variant='flush'>
                                <ListGroup.Item>
                                    <h2>Shipping</h2>
                                    <p><strong>Name: </strong> {order.user.name}</p>
                                    <p><strong>Email: </strong><a href={`mailto:${order.user.email}`}>{order.user.email}</a></p>
                                    <p>
                                        <strong>Shipping: </strong>
                                        {order.shippingAddress.address},  {order.shippingAddress.city}
                                        {'  '}
                                        {order.shippingAddress.postalCode},
                                {'  '}
                                        {order.shippingAddress.country}
                                    </p>

                                    {order.isDelivered ? (
                                        <Message variant='success'>Delivered on {order.deliveredAt}</Message>
                                    ) : (
                                            <Message variant='warning'>Not Delivered</Message>
                                        )}
                                </ListGroup.Item>

                                <ListGroup.Item>
                                    <h2>Payment Method</h2>
                                    <p>
                                        <strong>Method: </strong>
                                        {order.paymentMethod}
                                    </p>
                                    {order.isPaid ? (
                                        <Message variant='success'>Paid on {order.paidAt}</Message>
                                    ) : (
                                            <Message variant='warning'>Not Paid</Message>
                                        )}

                                </ListGroup.Item>

                                <ListGroup.Item>
                                    <h2>Order Items</h2>
                                    {order.orderItems.length === 0 ? <Message variant='info'>
                                        Order is empty
                            </Message> : (
                                            <ListGroup variant='flush'>
                                                {order.orderItems.map((item, index) => (
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
                                            <Col>$ {order.itemsPrice}</Col>
                                        </Row>
                                    </ListGroup.Item>

                                    <ListGroup.Item>
                                        <Row>
                                            <Col>Shipping:</Col>
                                            <Col>$ {order.shippingPrice}</Col>
                                        </Row>
                                    </ListGroup.Item>

                                    <ListGroup.Item>
                                        <Row>
                                            <Col>Tax:</Col>
                                            <Col>$ {order.taxPrice}</Col>
                                        </Row>
                                    </ListGroup.Item>

                                    <ListGroup.Item>
                                        <Row>
                                            <Col>Total:</Col>
                                            <Col>$ {order.totalPrice}</Col>
                                        </Row>
                                    </ListGroup.Item>


                                    {!order.isPaid && order.paymentMethod !== 'COD' && (
                                        <ListGroup.Item>
                                            {loadingPay && <Loader />}

                                            {order.shippingAddress.country &&
                                                order.shippingAddress.country.trim().toLowerCase() !== 'pakistan' && (
                                                    <>
                                                        {!sdkReady ? (
                                                            <Loader />
                                                        ) : (
                                                                <PayPalButton
                                                                    amount={order.totalPrice}
                                                                    onSuccess={successPaymentHandler}
                                                                />
                                                            )}
                                                        <hr />
                                                    </>
                                                )}

                                            <h5 style={{ marginBottom: '15px' }}>
                                                {order.shippingAddress.country &&
                                                    order.shippingAddress.country.trim().toLowerCase() !== 'pakistan'
                                                    ? 'Or Pay with Debit / Credit Card'
                                                    : 'Pay with Debit / Credit Card'}
                                            </h5>
                                            {cardError && <Message variant='danger'>{cardError}</Message>}
                                            <Form onSubmit={cardPaymentHandler}>
                                                <Form.Group controlId='cardNumber' className='mb-2'>
                                                    <Form.Label>Card Number</Form.Label>
                                                    <Form.Control
                                                        type='text'
                                                        placeholder='1234 5678 9012 3456'
                                                        maxLength={19}
                                                        value={cardNumber}
                                                        onChange={(e) => setCardNumber(e.target.value)}
                                                    ></Form.Control>
                                                </Form.Group>

                                                <Form.Group controlId='cardName' className='mb-2'>
                                                    <Form.Label>Name on Card</Form.Label>
                                                    <Form.Control
                                                        type='text'
                                                        placeholder='John Doe'
                                                        value={cardName}
                                                        onChange={(e) => setCardName(e.target.value)}
                                                    ></Form.Control>
                                                </Form.Group>

                                                <Row>
                                                    <Col>
                                                        <Form.Group controlId='cardExpiry' className='mb-2'>
                                                            <Form.Label>Expiry (MM/YY)</Form.Label>
                                                            <Form.Control
                                                                type='text'
                                                                placeholder='12/28'
                                                                maxLength={5}
                                                                value={cardExpiry}
                                                                onChange={(e) => setCardExpiry(e.target.value)}
                                                            ></Form.Control>
                                                        </Form.Group>
                                                    </Col>
                                                    <Col>
                                                        <Form.Group controlId='cardCvv' className='mb-2'>
                                                            <Form.Label>CVV</Form.Label>
                                                            <Form.Control
                                                                type='text'
                                                                placeholder='123'
                                                                maxLength={4}
                                                                value={cardCvv}
                                                                onChange={(e) => setCardCvv(e.target.value)}
                                                            ></Form.Control>
                                                        </Form.Group>
                                                    </Col>
                                                </Row>

                                                <Button type='submit' variant='dark' className='btn-block' style={{ width: '100%', marginTop: '10px' }}>
                                                    Pay $ {order.totalPrice}
                                                </Button>
                                            </Form>
                                        </ListGroup.Item>
                                    )}

                                    {!order.isPaid && order.paymentMethod === 'COD' && (
                                        <ListGroup.Item>
                                            <Message variant='info'>
                                                Pay in cash when your order is delivered
                                            </Message>
                                        </ListGroup.Item>
                                    )}
                                </ListGroup>
                                {loadingDeliver && <Loader />}
                                {userInfo && userInfo.isAdmin && order.isPaid && !order.isDelivered && (
                                    <ListGroup.Item>
                                        <Button
                                            type='button'
                                            className='btn btn-block'
                                            onClick={deliverHandler}
                                        >
                                            Mark As Delivered
                                        </Button>
                                    </ListGroup.Item>
                                )}
                            </Card>
                        </Col>
                    </Row>

                    <Modal
                        show={showPaidModal}
                        onHide={handleContinueShopping}
                        centered
                        backdrop="static"
                    >
                        <Modal.Body style={{ textAlign: 'center', padding: '40px 30px' }}>
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
                                {order.paymentMethod === 'COD' ? 'Order Confirmed!' : 'Payment Successful!'}
                            </h3>

                            <p style={{ color: '#6c757d', fontSize: '15px', marginBottom: '6px' }}>
                                {order.paymentMethod === 'COD'
                                    ? 'Your order has been placed. Pay in cash when it is delivered.'
                                    : 'Your order has been confirmed and paid.'}
                            </p>
                            <p style={{ color: '#6c757d', fontSize: '14px', marginBottom: '20px' }}>
                                Order ID: #{order._id}
                            </p>

                            <Button
                                variant="success"
                                onClick={handleContinueShopping}
                                style={{ minWidth: '180px' }}
                            >
                                Continue Shopping
                            </Button>
                        </Modal.Body>
                    </Modal>
                </div>
            )
}

export default OrderScreen