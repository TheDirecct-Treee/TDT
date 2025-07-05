import React from 'react';
import { Link } from 'react-router-dom';

const TermsAndConditions = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-amber-50 py-8">
      <div className="container mx-auto px-6 max-w-4xl">
        <div className="bg-white rounded-xl shadow-lg p-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-8 text-center">
            Terms and Conditions
          </h1>
          
          <div className="text-sm text-gray-600 mb-6">
            <strong>Last updated:</strong> January 2025
          </div>

          <div className="space-y-6 text-gray-700">
            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">1. Acceptance of Terms</h2>
              <p>
                By accessing and using The Direct Tree platform ("Service"), you accept and agree to be bound by the terms and provision of this agreement. If you do not agree to abide by the above, please do not use this service.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">2. Service Description</h2>
              <p>
                The Direct Tree is a business directory platform connecting customers with licensed businesses across the Bahamas. Our services include:
              </p>
              <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
                <li>Business directory listings</li>
                <li>Customer review and rating system</li>
                <li>Appointment booking services</li>
                <li>Event listing platform</li>
                <li>Photo gallery services</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">3. Business Owner Obligations</h2>
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-700">3.1 License Requirements</h3>
                <p>
                  All business owners must provide valid Bahamas government business licenses. Failure to maintain valid licensing may result in immediate account suspension.
                </p>
                
                <h3 className="text-lg font-semibold text-gray-700">3.2 Subscription Fees</h3>
                <p>
                  Business subscriptions are $20 USD per month with a 7-day trial period. Fees are non-refundable except as required by law.
                </p>
                
                <h3 className="text-lg font-semibold text-gray-700">3.3 Accurate Information</h3>
                <p>
                  Business owners must provide accurate, current, and complete information about their services, contact details, and business operations.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">4. Event Listings</h2>
              <p>
                Event organizers may list events for $5 USD per event per day. All events must comply with local laws and regulations. The Direct Tree reserves the right to remove inappropriate content.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">5. User Conduct</h2>
              <p>Users agree not to:</p>
              <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
                <li>Post false, misleading, or inappropriate content</li>
                <li>Impersonate other individuals or businesses</li>
                <li>Use the platform for illegal activities</li>
                <li>Attempt to circumvent security measures</li>
                <li>Spam or harass other users</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">6. Reviews and Ratings</h2>
              <div className="space-y-2">
                <p>
                  Users may leave honest reviews based on their experiences. The Direct Tree reserves the right to moderate and remove reviews that violate our community guidelines.
                </p>
                <p>
                  Fake reviews, review manipulation, or incentivized reviews are strictly prohibited and may result in account termination.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">7. Payment Terms</h2>
              <div className="space-y-2">
                <p>
                  All payments are processed through PayPal. By using our payment services, you agree to PayPal's terms and conditions.
                </p>
                <p>
                  Subscription fees are billed monthly in advance. Event listing fees are charged immediately upon posting.
                </p>
                <p>
                  Refunds may be provided at our discretion for technical issues or extraordinary circumstances.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">8. Intellectual Property</h2>
              <p>
                The Direct Tree platform, including its design, functionality, and content, is protected by copyright and other intellectual property laws. Users retain ownership of their uploaded content but grant us a license to display it on our platform.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">9. Privacy and Data Protection</h2>
              <p>
                Your privacy is important to us. Please review our <Link to="/privacy-policy" className="text-green-600 hover:text-green-800 underline">Privacy Policy</Link> to understand how we collect, use, and protect your information.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">10. Account Termination</h2>
              <p>
                We reserve the right to suspend or terminate accounts that violate these terms, engage in fraudulent activity, or pose a risk to our platform or users.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">11. Limitation of Liability</h2>
              <p>
                The Direct Tree serves as a platform connecting businesses and customers. We are not responsible for the quality of services provided by listed businesses or the accuracy of user-generated content.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">12. Governing Law</h2>
              <p>
                These terms are governed by the laws of the Commonwealth of The Bahamas. Any disputes will be resolved in the courts of Nassau, New Providence.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">13. Changes to Terms</h2>
              <p>
                We reserve the right to modify these terms at any time. Users will be notified of significant changes via email or platform notifications.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">14. Contact Information</h2>
              <p>
                For questions about these terms, please contact us at:
              </p>
              <div className="ml-4 mt-2">
                <p>Email: legal@direct-tree.com</p>
                <p>Website: https://direct-tree.com</p>
              </div>
            </section>
          </div>

          <div className="mt-8 pt-6 border-t border-gray-200">
            <div className="flex justify-between items-center">
              <Link 
                to="/register" 
                className="text-green-600 hover:text-green-800 font-semibold"
              >
                ← Back to Registration
              </Link>
              <Link 
                to="/privacy-policy" 
                className="bg-gradient-to-r from-green-600 to-amber-600 text-white px-6 py-2 rounded-lg hover:from-green-700 hover:to-amber-700 transition-all"
              >
                View Privacy Policy →
              </Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TermsAndConditions;