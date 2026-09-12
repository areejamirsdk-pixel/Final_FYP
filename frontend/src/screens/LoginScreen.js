import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Form, Button, Row, Col } from 'react-bootstrap'
import { useDispatch, useSelector } from 'react-redux'
import Loader from '../components/Loader'
import Message from '../components/Message'
import FormContainer from '../components/FormContainer'
import { requestOtp, verifyOtp } from '../actions/userActions'

function LoginScreen({ location, history }) {
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [otp, setOtp] = useState('')

    const dispatch = useDispatch()

    const redirect = location.search ? location.search.split('=')[1] : '/'

    const userOtp = useSelector(state => state.userOtp)
    const { loading: otpLoading, error: otpError, otpSent, email: otpEmail } = userOtp

    const userLogin = useSelector(state => state.userLogin)
    const { error: loginError, loading: loginLoading, userInfo } = userLogin

    useEffect(() => {
        if (userInfo) {
            history.push(redirect)
        }
    }, [history, userInfo, redirect])

    const submitCredentials = (e) => {
        e.preventDefault()
        dispatch(requestOtp(email, password))
    }

    const submitOtp = (e) => {
        e.preventDefault()
        dispatch(verifyOtp(otpEmail, otp))
    }

    return (
        <FormContainer>
            <h1>Sign In</h1>

            {!otpSent ? (
                <>
                    {otpError && <Message variant='danger'>{otpError}</Message>}
                    {otpLoading && <Loader />}
                    <Form onSubmit={submitCredentials}>
                        <Form.Group controlId='email'>
                            <Form.Label>Email Address</Form.Label>
                            <Form.Control
                                type='email'
                                placeholder='Enter Email'
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                            >
                            </Form.Control>
                        </Form.Group>

                        <Form.Group controlId='password'>
                            <Form.Label>Password</Form.Label>
                            <Form.Control
                                type='password'
                                placeholder='Enter Password'
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                            >
                            </Form.Control>
                        </Form.Group>

                        <Button type='submit' variant='primary'>
                            Sign In
                        </Button>
                    </Form>

                    <Row className='py-3'>
                        <Col>
                            New Customer? <Link
                                to={redirect ? `/register?redirect=${redirect}` : '/register'}>
                                Register
                                </Link>
                        </Col>
                    </Row>
                </>
            ) : (
                <>
                    <Message variant='success'>
                        A 6-digit code was sent to {otpEmail}
                    </Message>
                    {loginError && <Message variant='danger'>{loginError}</Message>}
                    {loginLoading && <Loader />}
                    <Form onSubmit={submitOtp}>
                        <Form.Group controlId='otp'>
                            <Form.Label>Enter Code</Form.Label>
                            <Form.Control
                                type='text'
                                placeholder='6-digit code'
                                maxLength={6}
                                value={otp}
                                onChange={(e) => setOtp(e.target.value)}
                            >
                            </Form.Control>
                        </Form.Group>

                        <Button type='submit' variant='primary'>
                            Verify & Sign In
                        </Button>
                    </Form>
                </>
            )}
        </FormContainer>
    )
}

export default LoginScreen