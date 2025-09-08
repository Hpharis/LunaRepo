# from powershell command line to start, .\run_deploy.ps1
Write-Host "🛠  Building TouringMag..."
npm run build

Write-Host "🚀 Deploying to Vercel..."
npx vercel deploy --prebuilt --prod

Write-Host "✅ Done! TouringMag is live."
