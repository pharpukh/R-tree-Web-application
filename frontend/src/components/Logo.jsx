import React from 'react';

const Logo = () => (
  // SVG logo with a circular gradient background, multiple ellipses representing leaves, and a centered letter "R"
  <svg
    width="60"
    height="60"
    viewBox="0 0 100 100"
    style={{ display: 'block' }}
  >
    <defs>
      <radialGradient id="blueGradient" cx="50%" cy="50%" r="50%">
        <stop offset="0%" stopColor="#BBDEFB" />
        <stop offset="100%" stopColor="#2196F3" />
      </radialGradient>
    </defs>
    <circle cx="50" cy="50" r="45" fill="url(#blueGradient)" />
    <g fill="#90CAF9">
      {/* Render multiple ellipses at various angles to simulate leaves */}
      {[0, 45, 90, 135, 180, 225, 270, 315].map((angle) => (
        <ellipse
          key={angle}
          cx="0"
          cy="-24"
          rx="5"
          ry="8"
          transform={`
            translate(50, 50)
            rotate(${angle})
          `}
        />
      ))}
    </g>
    <text
      x="50"
      y="65"
      fontSize="40"
      textAnchor="middle"
      fill="white"
      fontWeight="bold"
      fontFamily="sans-serif"
    >
      R
    </text>
  </svg>
);

export default Logo;
