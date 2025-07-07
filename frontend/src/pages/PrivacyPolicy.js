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
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">1. Introduction</h2>
              <p>
                The Direct Tree ("we," "our," or "us") is committed to protecting your privacy and personal information. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our business directory platform and related services in accordance with the laws of the Commonwealth of The Bahamas.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">2. Information We Collect</h2>
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-700">2.1 Personal Information</h3>
                <p>We collect personal information that you provide directly to us, including:</p>
                <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
                  <li>Name, email address, and phone number</li>
                  <li>Business information (for business owners)</li>
                  <li>Government business license documents</li>
                  <li>Payment information processed through PayPal</li>
                  <li>Account credentials and authentication data</li>
                </ul>
                
                <h3 className="text-lg font-semibold text-gray-700">2.2 User-Generated Content</h3>
                <p>Information you create or upload to our platform:</p>
                <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
                  <li>Business profiles and descriptions</li>
                  <li>Photos and multimedia content</li>
                  <li>Reviews and ratings</li>
                  <li>Event listings and promotional content</li>
                  <li>FAQ responses and customer communications</li>
                </ul>

                <h3 className="text-lg font-semibold text-gray-700">2.3 Technical Information</h3>
                <p>We automatically collect certain technical information:</p>
                <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
                  <li>IP address and device information</li>
                  <li>Browser type and version</li>
                  <li>Usage patterns and platform interactions</li>
                  <li>Location data (with your consent)</li>
                </ul>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">3. How We Use Your Information</h2>
              <p>We use your information for the following purposes:</p>
              <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
                <li>Providing and maintaining our business directory services</li>
                <li>Verifying business licenses and authenticity</li>
                <li>Processing payments and subscriptions</li>
                <li>Sending transactional emails and notifications</li>
                <li>Facilitating appointments and customer communications</li>
                <li>Moderating content and preventing fraudulent activity</li>
                <li>Improving our platform and user experience</li>
                <li>Complying with legal obligations under Bahamas law</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">4. Information Sharing and Disclosure</h2>
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-700">4.1 Public Information</h3>
                <p>
                  Business profiles, reviews, and event listings are publicly accessible as part of our directory service. You can control the visibility of certain information through your account settings.
                </p>
                
                <h3 className="text-lg font-semibold text-gray-700">4.2 Service Providers</h3>
                <p>We share information with trusted third-party service providers:</p>
                <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
                  <li><strong>PayPal</strong> - For payment processing and subscription management</li>
                  <li><strong>Cloudinary</strong> - For photo storage and optimization</li>
                  <li><strong>Mailgun</strong> - For email delivery and notifications</li>
                  <li><strong>Cloud hosting providers</strong> - For platform infrastructure</li>
                </ul>

                <h3 className="text-lg font-semibold text-gray-700">4.3 Legal Requirements</h3>
                <p>
                  We may disclose your information when required by law, including compliance with Bahamas regulatory authorities, court orders, or government requests.
                </p>

                <h3 className="text-lg font-semibold text-gray-700">4.4 Business Transfers</h3>
                <p>
                  In the event of a merger, acquisition, or sale of assets, your information may be transferred to the new entity, subject to the same privacy protections.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">5. Data Security</h2>
              <p>
                We implement appropriate technical and organizational security measures to protect your personal information against unauthorized access, alteration, disclosure, or destruction. This includes:
              </p>
              <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
                <li>Encryption of sensitive data in transit and at rest</li>
                <li>Regular security audits and vulnerability assessments</li>
                <li>Access controls and authentication mechanisms</li>
                <li>Secure cloud infrastructure and data centers</li>
                <li>Regular backups and disaster recovery procedures</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">6. Data Retention</h2>
              <p>
                We retain your personal information for as long as necessary to fulfill the purposes outlined in this policy, unless a longer retention period is required by law. Specific retention periods include:
              </p>
              <ul className="list-disc list-inside ml-4 mt-2 space-y-1">
                <li>Account information - Until account deletion plus 1 year</li>
                <li>Business licenses - 7 years for regulatory compliance</li>
                <li>Payment records - 7 years for tax and financial reporting</li>
                <li>Reviews and ratings - Permanently (anonymized after account deletion)</li>
                <li>Technical logs - 12 months for security and troubleshooting</li>
              </ul>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">7. Your Rights and Choices</h2>
              <div className="space-y-3">
                <h3 className="text-lg font-semibold text-gray-700">7.1 Access and Correction</h3>
                <p>
                  You have the right to access, update, or correct your personal information through your account settings or by contacting us directly.
                </p>
                
                <h3 className="text-lg font-semibold text-gray-700">7.2 Data Portability</h3>
                <p>
                  You can request a copy of your personal data in a structured, commonly used format.
                </p>
                
                <h3 className="text-lg font-semibold text-gray-700">7.3 Account Deletion</h3>
                <p>
                  You can request deletion of your account and associated personal information, subject to legal retention requirements.
                </p>

                <h3 className="text-lg font-semibold text-gray-700">7.4 Marketing Communications</h3>
                <p>
                  You can opt out of promotional emails at any time by using the unsubscribe link or contacting us directly.
                </p>
              </div>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">8. Cookies and Tracking</h2>
              <p>
                We use cookies and similar tracking technologies to enhance your experience and analyze platform usage. You can control cookie preferences through your browser settings, though this may limit certain platform functionality.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">9. International Data Transfers</h2>
              <p>
                Your information may be transferred to and processed in countries outside The Bahamas, including the United States, where our service providers are located. We ensure appropriate safeguards are in place to protect your data during such transfers.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">10. Children's Privacy</h2>
              <p>
                Our services are not intended for individuals under the age of 18. We do not knowingly collect personal information from children under 18. If you believe we have collected information from a child, please contact us immediately.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">11. Changes to This Policy</h2>
              <p>
                We may update this Privacy Policy from time to time to reflect changes in our practices or legal requirements. We will notify you of material changes through email or platform notifications. Your continued use of our services after such changes constitutes acceptance of the updated policy.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">12. Bahamas Data Protection Laws</h2>
              <p>
                This Privacy Policy is designed to comply with the Data Protection Act of The Bahamas and other applicable privacy laws. We are committed to handling your personal information in accordance with these legal requirements and best practices.
              </p>
            </section>

            <section>
              <h2 className="text-2xl font-semibold text-gray-800 mb-4">13. Contact Information</h2>
              <p>
                If you have questions about this Privacy Policy or our data practices, please contact us at:
              </p>
              <div className="ml-4 mt-2">
                <p>Email: privacy@direct-tree.com</p>
                <p>Website: https://direct-tree.com</p>
                <p>Address: Nassau, New Providence, The Bahamas</p>
              </div>
              <p className="mt-3">
                For data protection concerns, you may also contact the Office of the Information and Privacy Commissioner of The Bahamas.
              </p>
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
                to="/terms" 
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