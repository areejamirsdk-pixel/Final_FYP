import React, { useState, useEffect } from 'react'
import { Form, Button } from 'react-bootstrap'
import { useDispatch, useSelector } from 'react-redux'
import FormContainer from '../components/FormContainer'
import CheckoutSteps from '../components/CheckoutSteps'
import Message from '../components/Message'
import { saveShippingAddress } from '../actions/cartActions'

const COUNTRIES = [
    'Afghanistan', 'Albania', 'Algeria', 'Andorra', 'Angola', 'Argentina', 'Armenia',
    'Australia', 'Austria', 'Azerbaijan', 'Bahamas', 'Bahrain', 'Bangladesh', 'Barbados',
    'Belarus', 'Belgium', 'Belize', 'Benin', 'Bhutan', 'Bolivia', 'Bosnia and Herzegovina',
    'Botswana', 'Brazil', 'Brunei', 'Bulgaria', 'Burkina Faso', 'Burundi', 'Cambodia',
    'Cameroon', 'Canada', 'Chad', 'Chile', 'China', 'Colombia', 'Costa Rica', 'Croatia',
    'Cuba', 'Cyprus', 'Czechia', 'Denmark', 'Djibouti', 'Dominican Republic', 'Ecuador',
    'Egypt', 'El Salvador', 'Estonia', 'Ethiopia', 'Fiji', 'Finland', 'France', 'Gabon',
    'Gambia', 'Georgia', 'Germany', 'Ghana', 'Greece', 'Guatemala', 'Guinea', 'Guyana',
    'Haiti', 'Honduras', 'Hungary', 'Iceland', 'India', 'Indonesia', 'Iran', 'Iraq',
    'Ireland', 'Israel', 'Italy', 'Jamaica', 'Japan', 'Jordan', 'Kazakhstan', 'Kenya',
    'Kuwait', 'Kyrgyzstan', 'Laos', 'Latvia', 'Lebanon', 'Lesotho', 'Liberia', 'Libya',
    'Liechtenstein', 'Lithuania', 'Luxembourg', 'Madagascar', 'Malawi', 'Malaysia',
    'Maldives', 'Mali', 'Malta', 'Mauritania', 'Mauritius', 'Mexico', 'Moldova', 'Monaco',
    'Mongolia', 'Montenegro', 'Morocco', 'Mozambique', 'Myanmar', 'Namibia', 'Nepal',
    'Netherlands', 'New Zealand', 'Nicaragua', 'Niger', 'Nigeria', 'North Korea',
    'North Macedonia', 'Norway', 'Oman', 'Pakistan', 'Palestine', 'Panama',
    'Papua New Guinea', 'Paraguay', 'Peru', 'Philippines', 'Poland', 'Portugal', 'Qatar',
    'Romania', 'Russia', 'Rwanda', 'Saudi Arabia', 'Senegal', 'Serbia', 'Sierra Leone',
    'Singapore', 'Slovakia', 'Slovenia', 'Somalia', 'South Africa', 'South Korea',
    'South Sudan', 'Spain', 'Sri Lanka', 'Sudan', 'Suriname', 'Sweden', 'Switzerland',
    'Syria', 'Taiwan', 'Tajikistan', 'Tanzania', 'Thailand', 'Togo', 'Trinidad and Tobago',
    'Tunisia', 'Turkey', 'Turkmenistan', 'Uganda', 'Ukraine', 'United Arab Emirates',
    'United Kingdom', 'United States', 'Uruguay', 'Uzbekistan', 'Venezuela', 'Vietnam',
    'Yemen', 'Zambia', 'Zimbabwe'
]

function ShippingScreen({ history }) {

    const cart = useSelector(state => state.cart)
    const { shippingAddress } = cart

    const dispatch = useDispatch()

    const [address, setAddress] = useState(shippingAddress.address)
    const [permanentAddress, setPermanentAddress] = useState(shippingAddress.permanentAddress)
    const [city, setCity] = useState(shippingAddress.city)
    const [postalCode, setPostalCode] = useState(shippingAddress.postalCode)
    const [country, setCountry] = useState(shippingAddress.country)
    const [message, setMessage] = useState('')

    // City: letters and spaces only
    const isValidName = (value) => /^[A-Za-z\s]{2,}$/.test((value || '').trim())

    // Address: needs at least one letter AND more than one word, so a
    // bare number ("12345") or a single nonsense word ("bmjbg") is
    // rejected. Note: this only checks the *format* looks like a real
    // address — actually confirming it exists would need a paid
    // address-lookup API (e.g. Google Address Validation), which is
    // beyond a client-side check.
    const isValidAddress = (value) => {
        const trimmed = (value || '').trim()
        if (trimmed.length < 8) return false
        if (!/[A-Za-z]/.test(trimmed)) return false
        if (trimmed.split(/\s+/).length < 2) return false
        return true
    }

    // Postal code: digits only, 4-8 characters
    const isValidPostalCode = (value) => /^\d{4,8}$/.test((value || '').trim())

    const submitHandler = (e) => {
        e.preventDefault()

        if (!isValidAddress(address)) {
            setMessage('Please enter a complete address (letters + numbers, e.g. "House 12 Street 4")')
            return
        }

        if (!isValidAddress(permanentAddress)) {
            setMessage('Please enter a complete permanent address (letters + numbers, e.g. "House 12 Street 4")')
            return
        }

        if (!isValidName(city)) {
            setMessage('City should only contain letters')
            return
        }

        if (!isValidPostalCode(postalCode)) {
            setMessage('Postal code should be numbers only (4-8 digits)')
            return
        }

        if (!country) {
            setMessage('Please select a country')
            return
        }

        setMessage('')
        dispatch(saveShippingAddress({ address, permanentAddress, city, postalCode, country }))
        history.push('/payment')
    }

    return (
        <FormContainer>
            <CheckoutSteps step1 step2 />
            <h1>Shipping</h1>
            {message && <Message variant='danger'>{message}</Message>}
            <Form onSubmit={submitHandler}>

                <Form.Group controlId='address'>
                    <Form.Label>Address</Form.Label>
                    <Form.Control
                        required
                        type='text'
                        placeholder='e.g. House 12, Street 4, Gulberg'
                        value={address ? address : ''}
                        onChange={(e) => setAddress(e.target.value)}
                    >
                    </Form.Control>
                </Form.Group>

                <Form.Group controlId='permanentAddress'>
                    <Form.Label>Permanent Address</Form.Label>
                    <Form.Control
                        required
                        type='text'
                        placeholder='e.g. House 12, Street 4, Gulberg'
                        value={permanentAddress ? permanentAddress : ''}
                        onChange={(e) => setPermanentAddress(e.target.value)}
                    >
                    </Form.Control>
                </Form.Group>


                <Form.Group controlId='city'>
                    <Form.Label>City</Form.Label>
                    <Form.Control
                        required
                        type='text'
                        placeholder='Enter city'
                        value={city ? city : ''}
                        onChange={(e) => setCity(e.target.value)}
                    >
                    </Form.Control>
                </Form.Group>

                <Form.Group controlId='postalCode'>
                    <Form.Label>Postal Code</Form.Label>
                    <Form.Control
                        required
                        type='text'
                        inputMode='numeric'
                        placeholder='e.g. 60000'
                        maxLength={8}
                        value={postalCode ? postalCode : ''}
                        onChange={(e) => setPostalCode(e.target.value)}
                    >
                    </Form.Control>
                </Form.Group>

                <Form.Group controlId='country'>
                    <Form.Label>Country</Form.Label>
                    <Form.Control
                        required
                        as='select'
                        value={country ? country : ''}
                        onChange={(e) => setCountry(e.target.value)}
                    >
                        <option value=''>Select country</option>
                        {COUNTRIES.map((c) => (
                            <option key={c} value={c}>{c}</option>
                        ))}
                    </Form.Control>
                </Form.Group>

                <Button type='submit' variant='primary'>
                    Continue
                </Button>
            </Form>
        </FormContainer>
    )
}

export default ShippingScreen