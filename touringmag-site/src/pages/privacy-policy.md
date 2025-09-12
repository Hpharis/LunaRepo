---
import BaseLayout from '../layouts/BaseLayout.astro';
const title = "Privacy Policy";
const description = "How H.W. Pharis and TouringMag collect and use your data—including cookies, analytics, advertising, and newsletter signups.";
---
<BaseLayout {title} {description}>
  <section class="max-w-3xl mx-auto py-12 text-gray-200">
    <h1 class="text-4xl font-bold text-orange-500 mb-6">Privacy Policy</h1>
    <p><em>Last updated: September 8, 2025</em></p>
    <p><strong>Publisher:</strong> H.W. Pharis on behalf of TouringMag</p>

    <h2 class="mt-8 text-2xl">1. Data We Collect</h2>
    <ul class="list-disc ml-6">
      <li><strong>Newsletter Signups:</strong> Your email address, only if you opt in.</li>
      <li><strong>Cookies & Tracking:</strong> Analytics and ad personalization (e.g., Google Analytics).</li>
      <li><strong>Affiliate Tracking:</strong> Used to track referrals and commissions.</li>
    </ul>

    <h2 class="mt-8 text-2xl">2. How We Use Your Data</h2>
    <p>We use data to send newsletters (if you opt in), improve site performance, and serve relevant ads across TouringMag and related sites.</p>

    <h2 class="mt-8 text-2xl">3. Third-Party Partners</h2>
    <p>Third parties like Google and ad networks may use cookies to deliver personalized ads. You can opt out via Google Ads Settings or <a href="https://aboutads.info/" class="text-orange-400">aboutads.info</a>. :contentReference[oaicite:0]{index=0}</p>

    <h2 class="mt-8 text-2xl">4. Cookies & Consent</h2>
    <p>You can manage or disable cookies in your browser settings. We use cookies for analytics, site functionality, preferences, and ad personalization. :contentReference[oaicite:1]{index=1}</p>

    <h2 class="mt-8 text-2xl">5. Your Rights</h2>
    <p>We respect your privacy rights under GDPR and CalOPPA. You can request access, correction, deletion, or withdraw consent anytime. :contentReference[oaicite:2]{index=2}</p>

    <h2 class="mt-8 text-2xl">6. Contact</h2>
    <p>Questions? Reach out at <a href="mailto:contact@touringmag.com" class="text-orange-400">contact@touringmag.com</a>.</p>

    <h2 class="mt-8 text-2xl">7. Updates to This Policy</h2>
    <p>We may update this policy—see this page for the latest version and date.</p>
  </section>
</BaseLayout>
