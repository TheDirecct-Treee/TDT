import React from 'react';
import { Link } from 'react-router-dom';

const PrivacyPolicy = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-amber-50 py-8">
      <div className="container mx-auto px-6 max-w-4xl">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">
            Privacy Policy
          </h1>
          
          <div className="text-sm text-gray-600 mb-6">
            <strong>Last updated:</strong> January 2025
          </div>

          <div className="space-y-6 text-gray-700">
            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">1. Information We Collect</h2>
              
              <h3 className="text-lg font-semibold text-gray-700 mb-2">1.1 Personal Information</h3>
              <p className="mb-3">When you register for The Direct Tree, we collect:</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Name and email address</li>
                <li>Phone number (optional)</li>
                <li>Password (encrypted)</li>
                <li>Account type (customer or business owner)</li>
              </ul>

              <h3 className="text-lg font-semibold text-gray-700 mb-2 mt-4">1.2 Business Information</h3>
              <p className="mb-3">For business accounts, we also collect:</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Business name and description</li>
                <li>Business category and location</li>
                <li>Contact information and hours</li>
                <li>Business license information</li>
                <li>Photos and service descriptions</li>
              </ul>

              <h3 className="text-lg font-semibold text-gray-700 mb-2 mt-4">1.3 Usage Data</h3>
              <p className="mb-3">We automatically collect:</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>IP address and browser information</li>
                <li>Pages visited and time spent</li>
                <li>Search queries and interactions</li>
                <li>Device and location data (with permission)</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">2. How We Use Your Information</h2>
              <p className="mb-3">We use your information to:</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Provide and improve our platform services</li>
                <li>Process payments and subscriptions</li>
                <li>Send important account and service notifications</li>
                <li>Connect customers with businesses</li>
                <li>Moderate content and prevent fraud</li>
                <li>Analyze usage patterns to enhance user experience</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">3. Information Sharing</h2>
              
              <h3 className="text-lg font-semibold text-gray-700 mb-2">3.1 Public Information</h3>
              <p className="mb-3">The following information is publicly visible:</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Business profiles and contact information</li>
                <li>Customer reviews (with name or anonymous option)</li>
                <li>Event listings and organizer details</li>
                <li>Photos uploaded to business galleries</li>
              </ul>

              <h3 className="text-lg font-semibold text-gray-700 mb-2 mt-4">3.2 Third-Party Services</h3>
              <p className="mb-3">We share data with trusted partners:</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li><strong>PayPal:</strong> Payment processing and subscription management</li>
                <li><strong>Cloudinary:</strong> Image storage and optimization</li>
                <li><strong>Mailgun:</strong> Email delivery services</li>
                <li><strong>Analytics providers:</strong> Anonymous usage statistics</li>
              </ul>

              <h3 className="text-lg font-semibold text-gray-700 mb-2 mt-4">3.3 Legal Requirements</h3>
              <p>We may disclose information when required by law or to protect our rights and users' safety.</p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">4. Data Security</h2>
              <p className="mb-3">We implement security measures including:</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Encrypted data transmission (SSL/TLS)</li>
                <li>Secure password hashing</li>
                <li>Regular security audits</li>
                <li>Access controls and monitoring</li>
                <li>Secure cloud infrastructure</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">5. Cookies and Tracking</h2>
              <p className="mb-3">We use cookies and similar technologies to:</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>Keep you logged in</li>
                <li>Remember your preferences</li>
                <li>Analyze site performance</li>
                <li>Provide personalized experiences</li>
              </ul>
              <p className="mt-3">You can control cookies through your browser settings.</p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">6. Your Rights and Choices</h2>
              <p className="mb-3">You have the right to:</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li><strong>Access:</strong> Request a copy of your personal data</li>
                <li><strong>Update:</strong> Correct inaccurate information</li>
                <li><strong>Delete:</strong> Request deletion of your account and data</li>
                <li><strong>Portability:</strong> Export your data in a common format</li>
                <li><strong>Opt-out:</strong> Unsubscribe from marketing communications</li>
              </ul>
              <p className="mt-3">Contact us at privacy@direct-tree.com to exercise these rights.</p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">7. Data Retention</h2>
              <p className="mb-3">We retain your data:</p>
              <ul className="list-disc list-inside ml-4 space-y-1">
                <li>As long as your account is active</li>
                <li>For legitimate business purposes</li>
                <li>As required by law</li>
                <li>Until you request deletion</li>
              </ul>
              <p className="mt-3">Deleted accounts are purged within 30 days, except for legal retention requirements.</p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">8. Children's Privacy</h2>
              <p>
                The Direct Tree is not intended for children under 18. We do not knowingly collect personal information from minors. If we discover such information, we will delete it immediately.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">9. International Data Transfers</h2>
              <p>
                Your data may be processed in countries outside the Bahamas, including the United States where our service providers are located. We ensure appropriate safeguards are in place.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">10. Changes to This Policy</h2>
              <p>
                We may update this privacy policy periodically. Significant changes will be notified via email or platform notifications. Continued use constitutes acceptance of the updated policy.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">11. Contact Us</h2>
              <p className="mb-3">For privacy-related questions or requests:</p>
              <div className="ml-4">
                <p><strong>Email:</strong> privacy@direct-tree.com</p>
                <p><strong>Website:</strong> https://direct-tree.com</p>
                <p><strong>Mail:</strong> The Direct Tree, Privacy Officer, Nassau, Bahamas</p>
              </div>
            </section>

            <section className="bg-green-50 p-4 rounded-lg">
              <h2 className="text-xl font-semibold text-green-800 mb-2">Your Privacy Matters</h2>
              <p className="text-green-700">
                At The Direct Tree, we're committed to protecting your privacy and being transparent about how we handle your data. If you have any concerns or questions, please don't hesitate to contact us.
              </p>
            </section>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <Link 
                to="/terms-and-conditions" 
                className="text-green-600 hover:text-green-800 font-semibold"
              >
                ← View Terms & Conditions
              </Link>
              <Link 
                to="/register" 
                className="bg-gradient-to-r from-green-600 to-amber-600 text-white px-6 py-2 rounded-lg hover:from-green-700 hover:to-amber-700 transition-all"
              >
                Back to Registration →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy;